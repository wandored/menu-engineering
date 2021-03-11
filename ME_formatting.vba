Sub casual_format()
    
    Dim sh As Long
    Dim ws As Worksheet
    Dim Rng As Range
    Dim C As Long
    Dim LR As Long
    Dim i As Long
    Dim wsht As Worksheet
    Dim firstRow As Long
    Dim lastRow As Long
    
            
    Categories = Array("Appetizer", "Salad", "Sandwich", "Entree", "Side", "Dessert", "Early Evening", "Brunch", "Kid Meal", "Add-On", "Beverage", "Special", "Catering", "No Charge", "Beer", "Wine", "Liquor", "Gift Card", "None")
    Sheet_Num = ActiveWorkbook.Sheets.Count
        
    
    For sh = ActiveSheet.Index To Sheets.Count
        Sheets(sh).Select
        Range("C:C,D:D,E:E,G:G,H:H,I:I").Select
        Selection.Style = "Currency"
        Columns("F:F").Select
        Selection.NumberFormat = "0.0%"
        Columns("A:L").Select
        Selection.Columns.AutoFit
        Set ws = ActiveSheet
        For Each Cell In ws.Columns(1).Cells
            If IsEmpty(Cell) = True Then Cell.Select: Exit For
        Next Cell
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
    
    Sheets ("No Charge")
        
    Sheets("Totals").Columns("J:L").Delete
    Sheets("Totals").Columns("C:E").Delete

    Set Rng = Sheets("Totals").Range("A1:A19").Find("Liquor")
    firstRow = Rng.Offset(-2, 0).Row
    lastRow = Rng.Row
    Rng.Offset(1, 0).Resize(3).EntireRow.Insert
    Rng.Offset(1, 0).Value = "Alcohol Total"
    Rng.Offset(1, 3).Formula = "=Sum(D" & firstRow & ":D" & lastRow & ")"
    Rng.Offset(1, 4).Formula = "=Sum(E" & firstRow & ":E" & lastRow & ")"
    Rng.Offset(1, 5).Formula = "=Sum(F" & firstRow & ":F" & lastRow & ")"
    Rng.Offset(1, 2).Formula = "=$E$" & lastRow + 1 & "/$D$" & lastRow + 1
    
    Set Rng = Sheets("Totals").Range("A1:A19").Find("No Charge")
    firstRow = 2
    lastRow = Rng.Row
    Rng.Offset(1, 0).Resize(3).EntireRow.Insert
    Rng.Offset(1, 0).Value = "Food Total"
    Rng.Offset(1, 3).Formula = "=Sum(D" & firstRow & ":D" & lastRow & ")"
    Rng.Offset(1, 4).Formula = "=Sum(E" & firstRow & ":E" & lastRow & ")"
    Rng.Offset(1, 5).Formula = "=Sum(F" & firstRow & ":F" & lastRow & ")"
    Rng.Offset(1, 2).Formula = "=$E$" & lastRow + 1 & "/$D$" & lastRow + 1
    
    Sheets("Totals").Columns.AutoFit
    
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

