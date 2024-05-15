from collections import UserDict
import re
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone_number):
        if not re.fullmatch(r"\d{10}", phone_number):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(phone_number)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(self.value)


class Record:
    """
    Represents a contact record with a name and a list of phones.

    Attributes:
        name (Name): The name of the contact.
        phones (list[Phone]): The list of phone numbers associated with the contact.
        birthday (Birthday): The birthday of the contact.
    """

    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = phones if phones else []
        self.birthday = birthday if birthday else None

    def add_phone(self, phone):
        """
        Adds a new phone number to the contact.

        Args:
            phone (str): The phone number to add.

        Returns:
            str: A message indicating whether the phone number was added successfully or if it already exists.
        """
        new_phone = Phone(phone)
        if new_phone in self.phones:
            return f"Phone {phone} already exists for {self.name.value}."
        self.phones.append(new_phone)
        return f"Phone {phone} added to {self.name.value}."

    def remove_phone(self, phone):
        """
        Removes a phone number from the contact.

        Args:
            phone (str): The phone number to remove.

        Returns:
            str: A message indicating whether the phone number was removed successfully.

        Raises:
            ValueError: If the specified phone number is not found in the contact.
        """
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return f"Phone {phone} removed."
        raise ValueError("Phone not found.")

    def edit_phone(self, old_phone, new_phone):
        """
        Edits a phone number in the contact.

        Args:
            old_phone (str): The old phone number to replace.
            new_phone (str): The new phone number to set.

        Returns:
            str: A message indicating whether the phone number was edited successfully.

        Raises:
            ValueError: If the specified old phone number is not found in the contact.
        """
        for idx, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return f"Phone {old_phone} changed to {new_phone}."
        raise ValueError("Old phone not found.")

    def find_phone(self, phone):
        """
        Finds a phone number in the contact.

        Args:
            phone (str): The phone number to find.

        Returns:
            Phone: The phone number object if found.

        Raises:
            ValueError: If the specified phone number is not found in the contact.
        """
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError("Phone not found.")

    def add_birthday(self, birthday):
        """
        Adds a birthday to the contact.

        Args:
            birthday (str): The birthday to add in format DD.MM.YYYY.

        Returns:
            str: A message indicating whether the birthday was added successfully.

        Raises:
            ValueError: If the specified birthday is in the wrong format.
        """
        try:
            self.birthday = Birthday(birthday)
            return f"Birthday {birthday} added to {self.name.value}."
        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = (
            self.birthday.value.strftime("%d.%m.%Y")
            if self.birthday
            else "No birthday set"
        )
        return (
            f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"
        )


class AddressBook(UserDict):
    """
    A class representing an address book.

    This class extends the UserDict class and provides additional methods for managing records in the address book.

    Attributes:
        data (dict): A dictionary to store the records in the address book.

    Methods:
        add_record(record): Adds a record to the address book.
        find(name): Finds a record by name in the address book.
        delete(name): Deletes a record by name from the address book.
        get_upcoming_birthdays(days): Retrieves a list of upcoming birthdays within the specified number of days.

    """

    def add_record(self, record):
        """
        Adds a record to the address book.

        If a record with the same name already exists, the phone numbers will be combined.

        Args:
            record (Record): The record to be added to the address book.

        Returns:
            str: A message indicating whether the record was added or if the phone numbers were combined.

        """
        if record.name.value in self.data:
            existing_record = self.data[record.name.value]
            existing_record.phones.extend(record.phones)
            return f"Record for {record.name.value} already exists. Phone numbers combined."
        self.data[record.name.value] = record

    def find(self, name):
        """
        Finds a record by name in the address book.

        Args:
            name (str): The name of the record to find.

        Returns:
            Record: The record with the specified name.

        Raises:
            KeyError: If a record with the specified name is not found.

        """
        if name in self.data:
            return self.data[name]
        raise KeyError(f"Record for {name} not found.")

    def delete(self, name):
        """
        Deletes a record by name from the address book.

        Args:
            name (str): The name of the record to delete.

        Returns:
            str: A message indicating whether the record was deleted.

        Raises:
            KeyError: If a record with the specified name is not found.

        """
        if name in self.data:
            del self.data[name]
            return f"Record for {name} deleted."
        raise KeyError(f"Record for {name} not found.")

    def get_upcoming_birthdays(self, days=7):
        """
        Retrieves a list of upcoming birthdays within the specified number of days.

        Args:
            days (int): The number of days to consider for upcoming birthdays. Default is 7.

        Returns:
            list: A list of names of records with upcoming birthdays.

        """
        try:
            today = datetime.today().date()
            upcoming_birthdays = []

            for record in self.data.values():
                if record.birthday:
                    birthday = record.birthday.value
                    birthday_this_year = datetime(
                        today.year, birthday.month, birthday.day
                    ).date()

                    if birthday_this_year < today:
                        birthday_this_year = datetime(
                            today.year + 1, birthday.month, birthday.day
                        ).date()

                    days_before_birthday = (birthday_this_year - today).days

                    if days_before_birthday <= days:
                        upcoming_birthdays.append(
                            (record.name.value, birthday_this_year)
                        )

            return upcoming_birthdays
        except Exception as e:
            print(f"An error occurred in get_upcoming_birthdays: {str(e)}")
            return []
