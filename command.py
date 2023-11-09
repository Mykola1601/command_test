
# HW 12


from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


from collections import UserDict
from datetime import date, datetime
import pickle
import sys
import re

file_name = 'book.bin'


def normalize_phone(phone):
    numbers = re.findall('\d+', str(phone))
    phone = (''.join(numbers))
    if len(phone) == 10:
        return phone
    else:
        return None


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        self.value = value


class Birthday(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        birthday = datetime.strptime(str(value), '%Y-%m-%d')
        self.__value = birthday.date()
        if not self.__value:
            raise ValueError(f"Invalid  format  birthday")

    def __str__(self):
        return str(self.value)


class Phone(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value
        # super().__init__(self.__value)  #???

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        self.__value = normalize_phone(value)
        if not self.__value:
            raise ValueError(f"Invalid phone number format != 10digit")

    def __eq__(self, __value: object) -> bool:
        return self.__value == __value.__value


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone)] if phone else []
        self.__birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone: str) -> None:
        new_phone = Phone(phone)
        if new_phone not in self.phones:
            self.phones.append(new_phone)
            return f"Phone number {phone} added"  # to contact {self.name}"
        print(f"Phone number {phone} present in contact {self.name}")

    def remove_phone(self, phone_number: str) -> None | str:
        phone = Phone(phone_number)
        if phone in self.phones:
            self.phones.remove(phone)
            return f'{phone_number} removed'
        return f'phone {phone_number} not found '

    def edit_phone(self, *args):
        old_phone = Phone(args[0])
        new_phone = Phone(args[1])
        if old_phone in self.phones:
            self.phones[self.phones.index(old_phone)] = new_phone
            return f'{old_phone} changed {new_phone}'
        else:
            raise ValueError(f'phone {args[0]} not found in the record')

    def find_phone(self, phone_number: str) -> Phone | str:
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        else:
            return (f'phone {phone_number} not found in the record')

    def days_to_birthday(self):
        if self.__birthday.value:
            current_date = date.today()
            birth_date = self.__birthday.value
            birth_date = datetime(
                year=current_date.year, month=birth_date.month, day=birth_date.day).date()
            delta = birth_date - current_date
            if delta.days >= 0:
                return (f"{delta.days} days to birthday")
            else:
                birth_date = datetime(
                    year=current_date.year+1, month=birth_date.month, day=birth_date.day).date()
                delta = birth_date - current_date
                return (f"{delta.days} days to birthday")
        else:
            return ('No birthday date')

    def add_birthday(self, birthday):
        try:
            self.__birthday = Birthday(birthday)
        except ValueError:
            return ('Error input - Enter birthday in format YYYY-mm-dd')

    def __str__(self):
        return f"Contact: {self.name.value}; phones: {'; '.join(p.value for p in self.phones)}{'; Birthday '+ str(self.__birthday.value) if self.__birthday else '' }{';  '+ Record.days_to_birthday(self) if self.__birthday else '' }"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[str(record.name)] = record
        self.idx = 0

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return None

    def delete(self, name):
        if self.data.get(name):
            self.data.pop(name)
            return f'{name} deleted'
        else:
            return f'No record {name}'

    def __iter__(self):
        self.lst = []
        for i in self.data.keys():
            self.lst.append(i)     # list of al contacts for iter
        return self

    def __next__(self):
        if self.idx < len(book.data):
            self.idx += 1
            return book.data[self.lst[self.idx-1]]
        else:
            self.idx = 0
            raise StopIteration

# ============================================================================================


# decor
def errors(func):
    def inner(*args):
        try:
            return func(*args)
        except:  # any errors
            return "Give me valid data !!!"
    return inner

# greetings


def greeting(_):
    return ("How can I help you?")

# add contact


@errors
def add(text=""):
    text = text.removeprefix("add ")  # remove command
    name = text.split()[0].title()  # get Name
    text = text.removeprefix(name.lower())  # remove Name
    if not len(text) > 9:
        return 'Enter valid  phone 10dig'
    phone = normalize_phone(text)
    if not phone:
        return 'Enter valid phone 10 dig'
    if not book.find(name):
        name = Record(name)
        name.add_phone(phone)
        book.add_record(name)
        return name.name.value+" saved with number " + phone
    name = book.find(name)
    name.add_phone(phone)
    book.add_record(name)
    return name.name.value+' added phone ' + phone


# add birthday
@errors
def birthday(text=""):
    text = text.removeprefix("birthday ")  # remove command
    name = text.split()[0].title()  # get Name
    text = text.removeprefix(name.lower())  # remove Name
    birthday = text.strip()
    if book.data.get(name):
        book.data[name].add_birthday(birthday)
        return book.data[name]
    else:
        return 'no '+name+' in book, add phone first'

# change contact if exist


@errors
def change(text=""):
    text = text.removeprefix("change ")
    name = text.split()[0].title()
    text = text.removeprefix(name.lower())
    if not len(text) > 9:
        return 'Enter valid name & phone'
    phone = normalize_phone(text)
    if not phone:
        return 'Enter valid phone'
    if name in book.data.keys():
        name = book.data[name]
        old_phone = name.phones[0].value  # name.phones.value
        name.edit_phone(old_phone, phone)
        return name.name.value+" change number to " + phone
    else:
        return (f"no {name} in phone book")

# search contact


def phone(text=""):
    text = text.removeprefix("phone ")
    name = text.split()[0].title()
    if name in book.data.keys():
        return book.data[name]
    else:
        return name+' not exist in phone book!!!'

# show all iter


def show_all(_):
    list = ''
    for cont in book:
        list += str(cont) + '\r\n'
    return list

# show digit


def show(text):
    text = text.removeprefix("show")
    text = text.strip()
    if text.isdigit():
        counter = int(text)
    count = counter
    for cont in book:
        print(cont)
        if count > 1:
            count -= 1
        else:
            input("Press Enter for next records >>>")
            count = counter
    return 'finish '


# little HELP
def help(_):
    return """ 
    "help" for help 
    "add" for add contact
    "find" for find in book
    "hi" or "hello" for greeting
    "birthday" to add birthday for contact 
    "change" for change number
    "phone" for look  phone in contact's phones
    "show all" to show all book
    "show" to show part of book    example = 'show 2' 
    "exit" or "close" or "good bye" for exit and save book in file
    """


# iter in book and compare with FIND_text
def find(text):
    text = text.removeprefix("find ")
    text = text.strip()
    if not len(text) > 2:
        return 'Enter more then 2 simbols to find'
    list = ''
    for cont in book:
        if text in str(cont).lower():
            list += str(cont) + '\r\n'
    return list if len(list) > 1 else 'Cant find it'


# exit program and save book to hhd
def exit(_):
    with open(file_name, 'wb') as file:
        pickle.dump(book, file)
    return sys.exit('Good bye!\n')


# add notes
def add_note():
    pass


# note_find
def note_find():
    pass


# notes_show
def notes_show():
    pass




# dict for commands
dic = {
    "add note": add_note,
    "notes show": notes_show,
    "note find": note_find,
    "help": help,
    "find ": find,
    "hi": greeting,
    "hello": greeting,
    "birthday ": birthday,  # adding birthday
    "add ": add,
    "change ": change,
    "phone ": phone,
    "show all": show_all,
    "show": show,            # show 2 -- for iter
    "exit": exit,
    "close": exit,
    "good bye": exit,
}


variants = []   # підказки
for i in dic.keys():
    variants.append(i)


# find command in text > return dict key
def find_command(text=""):
    text = text.lower()
    for kee in dic.keys():
        if kee in text:
            return kee
    return None


book = AddressBook()

# # load contacts from file
try:
    with open(file_name, 'rb') as file:
        book = pickle.load(file)
        print('Book loadeed from file ')
except:
    print('No book file yet')


def main():
    # book.load()
    print("I'm Phone_Book_BOT, HELLO!!!")

    # Створення об'єкта WordCompleter для автодоповнення
    completer = WordCompleter(variants)

    # loop forever
    while True:
        user_input = (prompt(">>>", completer=completer))
        comand = find_command(user_input)
        if not comand:
            print("Do not undestend, try again")
        else:
            out = dic[comand](user_input)
            print(out)


# ========================================

if __name__ == "__main__":
    main()


# "exit" or "close" or "good bye" for SAVE book changes in file !!!!!!!
#  "help" for help
