import csv
import os
from abc import ABC, abstractmethod


class SingletonMeta(type):
    """Синглтон метакласс для Database."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    """Класс-синглтон базы данных с таблицами, хранящимися в файлах."""

    def __init__(self):
        self.tables = {}

    def register_table(self, table_name, table):
        self.tables[table_name] = table

    def insert(self, table_name, data):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist.")
        self.tables[table_name].add_record(data)

    def select(self, table_name, *args):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist.")
        return self.tables[table_name].filter(*args)

    def join(self, left_table, right_table, left_field, right_field):
        if left_table not in self.tables or right_table not in self.tables:
            raise ValueError("One or both tables do not exist.")
        results = []
        for l_rec in self.tables[left_table].records:
            for r_rec in self.tables[right_table].records:
                if l_rec[left_field] == r_rec[right_field]:
                    merged = {**l_rec, **r_rec}
                    results.append(merged)
        return results

    def multi_join(self, table_names, join_conditions):
        # Объединяет произвольное число таблиц
        if len(join_conditions) != len(table_names) - 1:
            raise ValueError(
                "The number of join conditions must be equal to the number of tables minus one."
            )

        if table_names[0] not in self.tables:
            raise ValueError(f"Table {table_names[0]} does not exist.")

        # Начинаем с записей первой таблицы
        result = self.tables[table_names[0]].records

        # Последовательно объединяем с оставшимися таблицами
        for i, table_name in enumerate(table_names[1:], start=1):
            if table_name not in self.tables:
                raise ValueError(f"Table {table_name} does not exist.")
            left_field, right_field = join_conditions[i - 1]
            new_result = []
            for rec in result:
                for next_rec in self.tables[table_name].records:
                    if rec.get(left_field) == next_rec.get(right_field):
                        merged = {**rec, **next_rec}
                        new_result.append(merged)
            result = new_result
        return result

    def aggregate(self, table, operation, column):
        # Определяем набор записей: либо по имени таблицы, либо уже готовый список
        if isinstance(table, str):
            if table not in self.tables:
                raise ValueError(f"Table {table} does not exist.")
            data = self.tables[table].records
        else:
            data = table
        try:
            values = [float(rec[column]) for rec in data if column in rec]
        except Exception:
            raise ValueError(f"Column {column} does not contain valid data.")
        if not values:
            raise ValueError(f"Column {column} does not contain valid data.")
        op = operation.lower()
        if op == "avg":
            return sum(values) / len(values)
        elif op == "max":
            return max(values)
        elif op == "min":
            return min(values)
        elif op == "count":
            return len(values)
        else:
            raise ValueError(f"Unknown aggregation method: {operation}")


class Table(ABC):
    """Абстрактный базовый класс для таблиц с вводом/выводом файлов CSV."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.records = []
        self.load()

    # Возвращает кортеж имён столбцов.
    @abstractmethod
    def schema(self):  # pragma: no cover
        pass

    # Возвращает значение ключа для проверки уникальности записи.
    @abstractmethod
    def unique_key(self, record):  # pragma: no cover
        pass

    # Метод для выборки записей по специфичным критериям.
    @abstractmethod
    def filter(self, *args):  # pragma: no cover
        pass

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, mode="r", newline="") as f:
                reader = csv.DictReader(f)
                self.records = [row for row in reader]
        else:
            self.records = []

    def save(self):
        with open(self.file_path, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.schema())
            writer.writeheader()
            writer.writerows(self.records)

    def add_record(self, data_line):
        values = data_line.split()
        new_entry = dict(zip(self.schema(), values))
        # Проверка на дублирование с учётом уникального ключа
        for rec in self.records:
            if self.unique_key(rec) == self.unique_key(new_entry):
                raise ValueError(f"Duplicate entry is not allowed: {new_entry}")
        self.records.append(new_entry)
        self.save()


class EmployeeTable(Table):
    def schema(self):
        return "e_id", "department_id", "name", "age", "salary"

    def unique_key(self, record):
        return record["e_id"], record["department_id"]

    def filter(self, start_id, end_id):
        return [rec for rec in self.records if start_id <= int(rec["e_id"]) <= end_id]


class DepartmentTable(Table):
    def schema(self):
        return "d_id", "department_name"

    def unique_key(self, record):
        return record["d_id"]

    def filter(self, dept_name):
        return [rec for rec in self.records if rec["department_name"] == dept_name]


class GoodsTable(Table):
    def schema(self):
        return "g_id", "product_name", "price", "category", "stock", "employee_id"

    def unique_key(self, record):
        return record["g_id"]

    def filter(self, price_threshold):
        # Возвращает список товаров, у которых цена больше заданного порога.
        return [rec for rec in self.records if float(rec["price"]) > price_threshold]
