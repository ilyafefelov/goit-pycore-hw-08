import pickle
from models import Field, Name, Phone, Birthday, Record, AddressBook
from typing import List, Tuple


AUTOSAVE_INTERVAL = 5  # Save after every 5 commands


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """Parses the user input and returns the command and arguments.

    Args:
        user_input (str): The user input to be parsed.

    Returns:
        tuple[str, list]: A tuple containing the command (str) and arguments (list).

    """
    if not user_input.split():
        return "Please enter a command:", []
    cmd, *args = user_input.split()

    return cmd, args


def input_error(func):
    """
    A decorator that handles common input errors and returns appropriate error messages.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.

    Raises:
        KeyError: If a contact is not found.
        ValueError: If an invalid command usage is detected.
        IndexError: If insufficient arguments are provided for a command.
    """

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return "Contact not found." + str(e)
        except ValueError as e:
            return "Invalid command usage." + str(e)
        except IndexError as e:
            return (
                "Invalid command usage. Insufficient arguments provided. Please provide all required information."
                + str(e)
            )

    return inner


import pickle


def save_data(book, filename="addressbook.pkl"):
    """
    Save the address book data to a file.

    Args:
        book (dict): The address book data to be saved.
        filename (str, optional): The name of the file to save the data to. Defaults to "addressbook.pkl".
    """
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    """
    Load data from a file.

    Args:
        filename (str): The name of the file to load data from. Defaults to "addressbook.pkl".

    Returns:
        AddressBook: The loaded address book if the file exists, otherwise a new address book.

    """
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return a new address book if the file is not found


@input_error
def add_contact(args, book: AddressBook) -> str:
    """Adds a new contact to the dictionary."""
    if len(args) < 2:
        raise ValueError("Please provide a name and at least one phone number.")

    name, *phones = args
    try:
        record = book.find(name)
        message = "Contact updated."
    except KeyError:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    for phone in phones:
        record.add_phone(phone)

    return f"{message} {name} with phones: {'; '.join(phones)}"


@input_error
def add_birthday(args, book):
    """Adds a birthday to a contact."""
    if len(args) != 2:
        raise ValueError(
            "Please provide the contact name and the birthday in format DD.MM.YYYY."
        )

    name, birthday = args
    record: Record = book.find(
        name
    )  # This will raise KeyError if not found, handled by the decorator
    return record.add_birthday(birthday)


@input_error
def change_contact(args, book):
    """
    Changes an existing contact's phone number.
    Assumes that args will contain the contact name, old phone number, and new phone number.
    """
    if len(args) != 3:
        raise ValueError(
            "Please provide the contact name, old phone number, and new phone number."
        )

    name, old_phone, new_phone = args
    record: Record = book.find(
        name
    )  # This will raise KeyError if not found, handled by the decorator
    return record.edit_phone(
        old_phone, new_phone
    )  # This will raise ValueError if old phone not found, also handled by the decorator


@input_error
def show_phone(args, book):
    """Shows a contact's phone numbers."""
    if len(args) != 1:
        raise ValueError("Please provide exactly one contact name `phone some_name`.")

    name = args[0]
    record = book.find(name)  # Will raise KeyError if not found, caught by decorator
    return f"{name}'s numbers are: {', '.join(phone.value for phone in record.phones)}"


@input_error
def show_all(book):
    """Displays all contacts."""
    if book.data:
        return "\n".join(str(record) for record in book.data.values())
    else:
        return "No contacts saved."


@input_error
def search_phone(args, book):
    """Searches for and shows all phone numbers of a specified contact."""
    if len(args) != 1:
        raise ValueError("Please provide exactly one contact name for the search.")

    name = args[0]
    record = book.find(name)  # Will raise KeyError if not found, handled by decorator
    if record.phones:
        return f"{name}'s numbers are: {', '.join(phone.value for phone in record.phones)} \
and his birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
    else:
        return f"No phone numbers found for {name}."


@input_error
def delete_contact(args, book):
    """Deletes a contact by name."""
    if len(args) != 1:
        raise ValueError("Please provide exactly one contact name to delete.")

    name = args[0]
    result = book.delete(name)
    return f"Contact {name} deleted successfully."


@input_error
def upcoming_birthdays(book):
    """Displays contacts with upcoming birthdays in the next 7 days."""
    birthdays: List[Tuple[str, date]] = book.get_upcoming_birthdays()
    if birthdays:
        upcoming_birthdays: List[str] = [
            f"{birthday[0]} ({birthday[1].strftime('%d.%m.%Y')})"
            for birthday in birthdays
        ]
        return "Upcoming birthdays: " + ", ".join(upcoming_birthdays)
    else:
        return "No upcoming birthdays."


@input_error
def show_birthday(args, book):
    """Shows a contact's birthday."""
    if len(args) != 1:
        raise ValueError(
            "Please provide exactly one contact name `show-birthday some_name`."
        )

    name = args[0]
    record = book.find(name)  # Will raise KeyError if not found, caught by decorator
    if record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
    else:
        return f"No birthday found for {name}."


def main():
    """
    The main function of the assistant bot program.

    This function initializes an empty dictionary to store contacts and then enters a loop to prompt the user for commands.
    The user can enter commands such as "hello", "add", "change", "phone", "all", "close", or "exit" to interact with the assistant bot.
    The function calls different helper functions based on the user's command and displays the corresponding output.
    The loop continues until the user enters "close" or "exit" to exit the program.
    """

    book = load_data()  # Load the address book data from a file
    command_count = 0  # Initialize a command count for autosaving

    print("Welcome. I am an assistant bot!")

    # Main loop to interact with the user
    while True:
        user_input = input("Enter a command: ").strip()  # Prompt the user for input

        if not user_input:  # Check if the user entered an empty string
            print("Please enter a command.")
            continue
        if user_input.lower() in ["close", "exit"]:  # Check if the user wants to exit
            print("Good bye!")
            save_data(book)
            break

        command, args = parse_input(user_input)

        # Helper functions to handle different commands
        def switch_commands(command):
            switcher = {
                "hello": "How can I help you?",
                "add": lambda: add_contact(args, book),
                "add-birthday": lambda: add_birthday(args, book),
                "show-birthday": lambda: show_birthday(args, book),
                "birthdays": lambda: upcoming_birthdays(book),
                "change": lambda: change_contact(args, book),
                "phone": lambda: show_phone(args, book),
                "all": lambda: show_all(book),
                "search": lambda: search_phone(args, book),
                "delete": lambda: delete_contact(args, book),
                "help": """ 
    add [ім'я] [**телефон]: Додати або новий контакт з іменем та телефонним номером, або телефонний номер к контакту який вже існує.
    change [ім'я] [старий телефон] [новий телефон]: Змінити телефонний номер для вказаного контакту.
    phone [ім'я]: Показати телефонні номери для вказаного контакту.
    all: Показати всі контакти в адресній книзі.
    add-birthday [ім'я] [дата народження]: Додати дату народження для вказаного контакту.
    show-birthday [ім'я]: Показати дату народження для вказаного контакту.
    birthdays: Показати дні народження, які відбудуться протягом наступного тижня.
    search [ім'я]: Search for contact.
    delete [ім'я]: Delete a contact.
    hello: Отримати вітання від бота.
    close або exit: Закрити програму.
                    """,
            }
            result = switcher.get(
                command,
                "Invalid command. Available commands: hello, add, add-birthday, show-birthday, birthdays, change, phone, all, search, delete, upcoming, close, exit & help",
            )
            return result() if callable(result) else result

        print(switch_commands(command))

        # Autosave the address book data after a certain number of commands
        command_count += 1
        if command_count >= AUTOSAVE_INTERVAL:
            save_data(book)
            print("Autosaved address book.")
            command_count = 0


if __name__ == "__main__":
    main()
