import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Tuple, Union

from django.db.models.query import QuerySet

from core.models import Booking, PricingRule
from core.utils.serializers import BookingPatchSerializer, BookingSerializer

logger = logging.getLogger(__name__)


@dataclass
class BookingService:

    booking_information: Union[BookingSerializer, BookingPatchSerializer]
    price: float = None

    def __post_init__(self):
        self._initial_process_booking()

    def process_booking(self) -> Booking:
        """process_booking processes the booking information and saves it to the database.

        Returns:
            Booking: The saved booking.
        """

        self._calculate_booking_price()

        return self._save_booking()

    def _initial_process_booking(self) -> None:
        """_initial_process_booking initialises the booking information."""

        self.data = self.booking_information.validated_data
        self.start_date = self.data["date_start"]
        self.end_date = self.data["date_end"]
        self.unprocessed_days_list = self._days_list_from_date_range(
            self.start_date, self.end_date
        )
        self.base_price = self.data["property"].base_price
        self.price = 0

    def _calculate_booking_price(self) -> None:
        """_calculate_booking_price calculates the total price of the booking."""

        self.stay_duration = self._calculate_stay_duration(self.start_date, self.end_date)

        (
            exact_day_and_duration_rules,
            exact_day_rules,
            duration_rules,
        ) = self._get_property_pricing_rules()

        if exact_day_and_duration_rules:
            self._process_exact_day_and_duration_pricing_rules(exact_day_and_duration_rules)

        if exact_day_rules:
            self._process_exact_day_rules(exact_day_rules)

        if duration_rules:
            self._process_duration_rules(duration_rules)
        logger.info(
            f'BookingService: Booking property {self.data["property"]}. Final price is {self.price}'
        )

    def _save_booking(self) -> Booking:
        """_save_booking saves the booking to the database.

        Returns:
            Booking: The saved booking.
        """

        if "id" in self.data:
            booking = Booking.objects.get(id=self.data["id"])
            saved_booking = self.booking_information.update(booking, self.data)
        else:
            saved_booking = self.booking_information.save()
        saved_booking.final_price = self.price
        Booking.save(saved_booking)

        return saved_booking

    def _process_duration_rules(self, query: QuerySet[PricingRule]) -> None:
        """_process_duration_rules applies duration pricing rules to the remainder of days after all other rules have been processed.

        Args:
            query (QuerySet[PricingRule]): The pricing rules corresponding to duration.
        """

        query = query.order_by("-min_stay_length")

        for rule in query:
            if self.stay_duration >= rule.min_stay_length:
                logger.info(
                    f"BookingService: Booking property {self.data['property']}. Applying duration rule on {len(self.unprocessed_days_list)} days."
                )
                # We need to make a copy of the list because its not safe to delete elemnts of a list while we iterate over it.
                days_to_process = list(self.unprocessed_days_list)
                for remaining_day in days_to_process:
                    self._apply_price_rule_to_day(rule)
                    self.unprocessed_days_list.remove(remaining_day)
                logger.info(f"Price so far {self.price}")
                break

    def _process_exact_day_rules(self, query: QuerySet[PricingRule]) -> None:
        """_process_exact_day_rules applies exact day pricing rules to the total price of the booking, prioritising based on fixed price first and price modifier afterwards.

        Args:
            query (QuerySet[PricingRule]): The pricing rules corresponding to exact day.
        """
        fixed_prices_subquery = query.filter(fixed_price__isnull=False).order_by("-fixed_price")
        modifier_prices_subquery = query.filter(fixed_price__isnull=True).order_by(
            "-price_modifier"
        )

        for rule in fixed_prices_subquery:
            if rule.specific_day in self.unprocessed_days_list:
                logger.info(
                    f"BookingService: Booking property {self.data['property']}. Applying exact day rule on {rule.specific_day}."
                )
                self._apply_price_rule_to_day(rule)
                self.unprocessed_days_list.remove(rule.specific_day)
                logger.info(f"Price so far {self.price}")

        for rule in modifier_prices_subquery:
            if rule.specific_day in self.unprocessed_days_list:
                logger.info(
                    f"BookingService: Booking property {self.data['property']}. Applying exact day rule on {rule.specific_day}."
                )
                self._apply_price_rule_to_day(rule)
                self.unprocessed_days_list.remove(rule.specific_day)
                logger.info(f"Price so far {self.price}")

    def _process_exact_day_and_duration_pricing_rules(self, query: QuerySet[PricingRule]) -> None:
        """_process_exact_day_and_duration_pricing_rules applies exact day and duration pricing rules to the total price of the booking,
        filtering and prioritising based on fixed price first and price modifier afterwards.

        Args:
            query (QuerySet[PricingRule]): The pricing rules corresponding to exact day and minimum stay length combined.
        """

        fixed_prices_subquery = query.filter(fixed_price__isnull=False).order_by("-fixed_price")
        modifier_prices_subquery = query.filter(fixed_price__isnull=True).order_by(
            "-price_modifier"
        )

        for rule in fixed_prices_subquery:
            if (
                rule.specific_day in self.unprocessed_days_list
                and self.stay_duration >= rule.min_stay_length
            ):
                logger.info(
                    f"BookingService: Booking property {self.data['property']}. Applying fixed price on day {rule.specific_day}."
                )
                self._apply_price_rule_to_day(rule)
                self.unprocessed_days_list.remove(rule.specific_day)
                logger.info(f"Price so far {self.price}")

        for rule in modifier_prices_subquery:
            if (
                rule.specific_day in self.unprocessed_days_list
                and self.stay_duration >= rule.min_stay_length
            ):
                logger.info(
                    f"BookingService: Booking property {self.data['property']}. Applying price modifier on day {rule.specific_day}."
                )
                self._apply_price_rule_to_day(rule)
                self.unprocessed_days_list.remove(rule.specific_day)
                logger.info(f"Price so far {self.price}")

    def _apply_price_rule_to_day(self, rule: PricingRule) -> None:
        """_apply_price_rule_to_day applies a pricing rule to the total price of the booking, for a particular day.

        Args:
            rule (PricingRule): The pricing rule to apply.
        """

        if getattr(rule, "fixed_price", False) and rule.fixed_price is not None:
            self.price += rule.fixed_price
        else:
            self.price += self.base_price * rule.price_modifier

    def _get_property_pricing_rules(self) -> Tuple[QuerySet[PricingRule]]:
        """_get_property_pricing_rules returns a tuple of pricing rules for the property,
        containing exact day and duration rules, exact day rules and duration rules.

        Returns:
            Tuple[QuerySet[PricingRule]]: Tuple of pricing rules for the property,
            containing exact day and duration rules, exact day rules and duration rules.
        """
        all_rules = PricingRule.objects.filter(property=self.data["property"])

        exact_day_and_duration_rules = all_rules.filter(
            specific_day__isnull=False, min_stay_length__isnull=False
        )
        exact_day_rules = all_rules.filter(
            specific_day__isnull=False, min_stay_length__isnull=True
        )
        duration_rules = all_rules.filter(specific_day__isnull=True, min_stay_length__isnull=False)

        return exact_day_and_duration_rules, exact_day_rules, duration_rules

    @staticmethod
    def _calculate_stay_duration(start_date: date, end_date: date) -> int:
        """_calculate_stay_duration calculates the number of days between two dates.

        Args:
            start_date (date): The start date of the stay.
            end_date (date): The end date of the stay.

        Returns:
            int: The number of days between the two dates.
        """
        return (end_date - start_date).days + 1

    @staticmethod
    def _day_is_in_range(day: date, start_date: date, end_date: date) -> bool:
        """_day_is_in_range checks if a day is in a date range.

        Args:
            day (date): The day to check.
            start_date (date): The start date of the range.
            end_date (date): The end date of the range.

        Returns:
            bool: True if the day is in the range, False otherwise.
        """
        return day >= start_date and day <= end_date

    @staticmethod
    def _days_list_from_date_range(start_date: date, end_date: date) -> List[date]:
        """_days_list_from_date_range returns a list of dates between start_date and end_date

        Args:
            start_date (date): The start date of the range.
            end_date (date): The end date of the range.

        Returns:
            List[date]: A list of dates between start_date and end_date.
        """
        return [start_date + timedelta(days=x) for x in range(0, (end_date - start_date).days + 1)]
