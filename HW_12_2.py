from collections import UserDict
from datetime import datetime, timedelta
import functools


class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not self._is_valid_phone(value):
            raise ValueError("Неправильний формат номера.")
        super().__init__(value)

    def _is_valid_phone(self):
        return len(str(self.value)) == 10


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def days_to_birthday(self):
        if self.birthday.value:
            today = datetime.today().date()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day).date()
            days_left = (next_birthday - today).days
            return days_left


class Birthday(Field):
    def __init__(self, value):
        if not self._is_valid_birthday(value):
            raise ValueError("Неправильный формат дня рождения.")
        super().__init__(value)

    def _is_valid_birthday(self):
        try:
            datetime.strptime(str(self.value), "%Y-%m-%d")
            return True
        except ValueError:
            return False


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def __iter__(self):
        return iter(self.data.values())

    def iterator(self, n):
        count = 0
        current_page = []
        for record in self:
            current_page.append(record)
            count += 1
            if count == n:
                yield current_page
                current_page = []
                count = 0
        if current_page:
            yield current_page

    def save(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(self.data, file)

    @classmethod
    def load(cls, file_path):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print("Файл не найден. Новая адресная книга не создана.")

    def search(self, query):
        search_results = []
        for record in self.data.values():
            if search_query in record.name.value or any(search_query in phone.value for phone in record.phones):
                search_results.append(record)
        return search_results

    def _record_contains_query(self, record, query):
        query = query.lower()
        if query in record.name.value.lower():
            return True
        for phone in record.phones:
            if query in str(phone.value):
                return True
        return False


contacts = AddressBook()


def input_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Контакт не найден"
        except ValueError:
            return "Неверный ввод. Пожалуйста, введите имя и телефон через пробел."
        except IndexError:
            return "Неверный ввод. Укажите имя."

    return wrapper


@input_error
def add_contact(name, phone):
    record = Record(name)
    record.add_phone(phone)
    contacts.add_record(record)
    return "Контакт успешно добавлен."


@input_error
def change_contact(name, phone):
    record = contacts.data.get(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return "Контакт успешно обновлен."
    raise KeyError


@input_error
def get_phone(name):
    record = contacts.data.get(name)
    if record:
        return record.phones[0].value
    raise KeyError


def show_all_contacts():
    if not contacts.data:
        return "Контакты не найдены."
    result = ""
    for record in contacts.data.values():
        result += f"{record.name.value}: "
        for phone in record.phones:
            result += f"{phone.value}, "
        result = result.rstrip(", ") + "\n"
    return result.strip()


def handle_command(command):
    if command.lower() == "hello":
        return "Могу я чем-нибудь помочь?"
    elif command.lower().startswith("add"):
        parts = command.split(" ", 2)
        if len(parts) < 3:
            raise ValueError
        name, phone = parts[1], parts[2]
        return add_contact(name, phone)
    elif command.lower().startswith("change"):
        parts = command.split(" ", 2)
        if len(parts) < 3:
            raise ValueError
        name, phone = parts[1], parts[2]
        return change_contact(name, phone)
    elif command.lower().startswith("phone"):
        parts = command.split(" ", 1)
        if len(parts) < 2:
            raise ValueError
        name = parts[1]
        return get_phone(name)
    elif command.lower() == "show all":
        return show_all_contacts()
    elif command.lower() in ["good bye", "close", "exit"]:
        return "До свидания!"
    else:
        return "Неверная команда. Пожалуйста, попробуйте еще раз."

def main():
    while True:
        command = input("Введите команду: ")
        response = handle_command(command)
        print(response)
        if response == "До свидания!":
            break

if __name__ == "__main__":
    main()
