import reminder as app
from reminder import Task
from click.testing import CliRunner

import datetime as dt

import pytest


@pytest.fixture
def task_list():
    return [
        Task(name='pay rent'),
        Task(name='buy bread'),
        Task(name='build cabin', deadline=dt.date(2025, 1, 1)),
        Task(name='update all software', deadline=dt.date(2000, 1, 1)),
    ]


def test_to_date():
    assert app._to_date('2022-09-01') == dt.date(2022, 9, 1)


def test_to_date_exception():
    with pytest.raises(ValueError, match='12345 is not in YYYY-MM-DD format.'):
        app._to_date('12345')


@pytest.mark.parametrize(
    'test_input, expected',
    [
        ('buy bread', Task(name='buy bread')),
        ('buy banana', None),
        (
            'PAY RENT',
            Task(name='pay rent'),
        ),
    ],
)
def test_find_task(test_input, expected, task_list):
    assert app._find_task(test_input, task_list) == expected


def test_save_load_task_list(task_list):
    app._save_task_list(task_list)
    load_list = app._get_task_list()
    assert task_list == load_list


def test_overdue(task_list):
    task = app._find_task('update all software', task_list)
    assert app._overdue(task.deadline)
    task = app._find_task('build cabin', task_list)
    assert not app._overdue(task.deadline)
    task = app._find_task('pay rent', task_list)
    assert not app._overdue(task.deadline)


def test_add_task(task_list):
    runner = CliRunner()
    result = runner.invoke(app.add, ['pay rent'])
    assert 'already in the list.' in result.output
    runner.invoke(app.add, ['do laundry'])
    assert Task(name='do laundry') in app._get_task_list()
    runner.invoke(app.add, ['add films to diary', '--deadline', '2023-12-25'])
    assert Task(name='add films to diary', deadline=dt.date(2023, 12, 25)) in app._get_task_list()


def test_list_tasks(task_list):
    runner = CliRunner()
    result = runner.invoke(app.list)
    for num, task in enumerate(task_list, start=1):
        assert f'{num}. {task.name}' in result.output


def test_remove(task_list):
    runner = CliRunner()
    runner.invoke(app.remove, ['update all software'])
    loaded = app._get_task_list()
    assert not Task(name='update all software') in loaded
