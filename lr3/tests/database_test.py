import os
import tempfile

import pytest
from database.database import Database, DepartmentTable, EmployeeTable, GoodsTable


@pytest.fixture
def temp_employee_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"e_id,department_id,name,age,salary\n")
        temp_file.write(b"1,201,John,35,45000\n")
        temp_file.write(b"2,202,Emily,28,48000\n")
        temp_file.close()
        yield temp_file.name
    os.remove(temp_file.name)


@pytest.fixture
def temp_department_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"d_id,department_name\n")
        temp_file.write(b"201,Accounting\n")
        temp_file.write(b"202,Legal_Department\n")
        temp_file.close()
        yield temp_file.name
    os.remove(temp_file.name)


@pytest.fixture
def temp_goods_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"g_id,product_name,price,category,stock,employee_id\n")
        temp_file.write(b"1,Product_A,1000.0,Electronics,15,1\n")
        temp_file.write(b"2,Product_B,750.0,Appliances,10,2\n")
        temp_file.close()
        yield temp_file.name
    os.remove(temp_file.name)


@pytest.fixture
def database(temp_employee_file, temp_department_file, temp_goods_file):
    db = Database()
    emp_table = EmployeeTable(temp_employee_file)
    emp_table.load()
    dept_table = DepartmentTable(temp_department_file)
    dept_table.load()
    goods_table = GoodsTable(temp_goods_file)
    goods_table.load()
    db.register_table("employees", emp_table)
    db.register_table("departments", dept_table)
    db.register_table("goods", goods_table)
    return db


def test_insert_select_employees(database):
    db = database
    db.insert("employees", "3 203 Michael 40 50000")
    employee_records = db.select("employees", 1, 3)
    assert len(employee_records) == 3
    employee_names = {record["name"] for record in employee_records}
    assert employee_names == {"John", "Emily", "Michael"}


def test_insert_select_departments(database):
    db = database
    db.insert("departments", "203 Finance")
    department_records = db.select("departments", "Accounting")
    assert len(department_records) == 1
    assert department_records[0]["department_name"] == "Accounting"


def test_insert_select_goods(database):
    db = database
    db.insert("goods", "3 Product_C 1200.0 Furniture 5 1")
    goods_records = db.select("goods", 1100.0)
    assert len(goods_records) == 1
    assert goods_records[0]["product_name"] == "Product_C"


def test_join_employees_departments(database):
    db = database
    joined_records = db.join("employees", "departments", "department_id", "d_id")
    department_names = {record["department_name"] for record in joined_records}
    assert department_names == {"Accounting", "Legal_Department"}


def test_multi_join(database):
    db = database
    multi_joined = db.multi_join(
        ["employees", "departments", "goods"],
        [("department_id", "d_id"), ("e_id", "employee_id")],
    )
    assert len(multi_joined) == 2
    product_names = {record["product_name"] for record in multi_joined}
    assert product_names == {"Product_A", "Product_B"}


def test_aggregate_employee_salaries(database):
    db = database
    avg_salary = db.aggregate("employees", "avg", "salary")
    max_salary = db.aggregate("employees", "max", "salary")
    min_salary = db.aggregate("employees", "min", "salary")
    count_salary = db.aggregate("employees", "count", "salary")
    assert avg_salary == 46500.0
    assert max_salary == 48000.0
    assert min_salary == 45000.0
    assert count_salary == 2
    with pytest.raises(ValueError, match="Unknown aggregation method: sum"):
        db.aggregate("employees", "sum", "salary")


def test_join_and_aggregate_goods(database):
    db = database
    joined_data = db.multi_join(
        ["employees", "departments", "goods"],
        [("department_id", "d_id"), ("e_id", "employee_id")],
    )
    max_price = db.aggregate(joined_data, "max", "price")
    goods_count = db.aggregate(joined_data, "count", "g_id")
    assert max_price == 1000.0
    assert goods_count == 2


def test_duplicate_inserts(database):
    db = database
    with pytest.raises(ValueError, match="Duplicate entry is not allowed"):
        db.insert("employees", "1 201 John 35 45000")
    with pytest.raises(ValueError, match="Duplicate entry is not allowed"):
        db.insert("departments", "201 HR_Department")
    with pytest.raises(ValueError, match="Duplicate entry is not allowed"):
        db.insert("goods", "1 Product_A 1000.0 Electronics 15 1")


def test_missing_table(database):
    with pytest.raises(ValueError, match="Table .* does not exist."):
        database.insert("unknown_table", "1 201 Test 30 40000")
    with pytest.raises(ValueError, match="Table .* does not exist."):
        database.select("unknown_table", "200")


def test_missing_table_for_join(database):
    with pytest.raises(ValueError, match="One or both tables do not exist."):
        database.join("employees", "test_department", "department_id", "d_id")
    with pytest.raises(ValueError, match="Table .* does not exist."):
        database.multi_join(["unknown_table", "unknown_table2"], [("a_id", "b_id")])
    with pytest.raises(ValueError, match="Table .* does not exist."):
        database.multi_join(
            ["employees", "unknown_table2"], [("department_id", "b_id")]
        )
    with pytest.raises(
        ValueError,
        match="The number of join conditions must be equal to the number of tables minus one.",
    ):
        database.multi_join(
            ["employees", "departments", "goods"], [("department_id", "d_id")]
        )


def test_aggregate_invalid_field(database):
    with pytest.raises(ValueError, match="Column .* does not contain valid data."):
        database.aggregate("employees", "avg", "test_field")
    with pytest.raises(ValueError, match="Table .* does not exist."):
        database.aggregate("unknown_table", "max", "a_id")
    with pytest.raises(ValueError, match="Column .* does not contain valid data."):
        database.aggregate("employees", "max", "name")


def test_load_table(database):
    test_table = EmployeeTable("")
    test_table.load()
    assert test_table.records == []
