# -*- coding: utf-8 -*-
from pdf_excel.html_table import html_table_to_grid


def test_simple_table():
    html = """
    <table>
      <tr><th>A</th><th>B</th></tr>
      <tr><td>1</td><td>2</td></tr>
    </table>
    """
    grid, issues = html_table_to_grid(html)
    assert issues == []
    assert grid == [["A", "B"], ["1", "2"]]


def test_colspan():
    html = """
    <table>
      <tr><td colspan="2">Header</td></tr>
      <tr><td>x</td><td>y</td></tr>
    </table>
    """
    grid, issues = html_table_to_grid(html)
    assert grid[0][0] == "Header"
    assert grid[0][1] == ""
    assert grid[1] == ["x", "y"]


def test_rowspan():
    html = """
    <table>
      <tr><td rowspan="2">R</td><td>a</td></tr>
      <tr><td>b</td></tr>
    </table>
    """
    grid, issues = html_table_to_grid(html)
    assert grid[0][0] == "R"
    assert grid[1][0] == ""
    assert grid[0][1] == "a"
    assert grid[1][1] == "b"


def test_empty_body():
    grid, issues = html_table_to_grid("")
    assert grid == []
    assert "empty HTML table_body" in issues[0]
