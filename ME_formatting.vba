Sub casual_format()

    Dim sh As Long
    Dim ws As Worksheet
    Dim Rng As Range
    Dim C As Long
    Dim LR As Long
    Dim i As Long
    Dim wsht As Worksheet

    Categories = Array("Appetizer", "Salad", "Sandwich", "Entree", "Side", "Kid Meal", "Dessert", "Add-On", "Beverage", "Beer", "Wine", "Liquor", "Gift Card", "Catering", "None")
    Sheet_Num = ActiveWorkbook.Sheets.Count


    For sh = ActiveSheet.Index To Sheets.Count
        Sheets(sh).Select
        Range("C:C,D:D,E:E,G:G,H:H,I:I").Select
        Selection.Style = "Currency"
        Columns("F:F").Select
        Selection.Style = "Percent"
        Columns("A:L").Select
        Selection.Columns.AutoFit
        Set ws = ActiveSheet
        For Each cell In ws.Columns(1).Cells
            If IsEmpty(cell) = True Then cell.Select: Exit For
        Next cell
        Selection.Value = ws.Name
    Next sh

    i = 1
    For Each cat In Categories
        If WorksheetExists((cat)) Then
            Sheets(cat).Move before:=Sheets(i)
            i = i + 1
        End If
    Next cat

    Sheets.Add.Name = "Totals"
    Sheets("Totals").Move before:=Sheets(1)

    ActiveWorkbook.Sheets("Appetizer").Range("A1").EntireRow.Copy Worksheets("Totals").Range("A1")

    i = 2
    C = Sheets.Count
    For C = 1 To C
        For Each cat In Categories
            If Sheets(C).Name = cat Then
                LR = Sheets(cat).Range("A" & Rows.Count).End(xlUp).Row
                Sheets(cat).Rows(LR).EntireRow.Copy
                Sheets("Totals").Rows(i).Insert
                i = i + 1
            End If
        Next cat
    Next C

    Sheets("Totals").Columns("J:L").Delete
    Sheets("Totals").Columns("C:E").Delete
    Sheets("Totals").Range("14:16").Insert
    Sheets("Totals").Range("11:14").Insert
    Sheets("Totals").Range("A11").Value = "Totals"
    Sheets("Totals").Range("A18").Value = "Totals"
    Sheets("Totals").Range("D11") = "=Sum(D2:D10)"
    Sheets("Totals").Range("D18") = "=Sum(D15:D17)"
    Sheets("Totals").Range("E11") = "=Sum(E2:E10)"
    Sheets("Totals").Range("E18") = "=Sum(E15:E17)"
    Sheets("Totals").Range("F11") = "=Sum(F2:F10)"
    Sheets("Totals").Range("F18") = "=Sum(F15:F17)"
    Sheets("Totals").Range("C11") = "=$E$11/$D$11"
    Sheets("Totals").Range("C18") = "=$E$18/$D$18"
    Sheets("Totals").Columns.AutoFit

'    Sheets("Totals").Range("A11:F11").Font.Bold
'    Sheets("Totals").Range("A18:F18").Font.Bold
'    Sheets("Totals").Range("A11:F11").Borders(xlEdgeBottom).LineStyle = XlLineStyle.xlContinuous
'    Sheets("Totals").Range("A18:F18").Borders(xlEdgeBottom).LineStyle = XlLineStyle.xlContinuous

End Sub

Function WorksheetExists(sh As String) As Boolean
    WorksheetExists = False
    For Each Sheet In Worksheets
        If sh = Sheet.Name Then
            WorksheetExists = True
            Exit Function
        End If
    Next Sheet
End Function

