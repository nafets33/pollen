from collections import defaultdict


class GridOptionsBuilder:

    def __init__(self):
        self.__grid_options: defaultdict = defaultdict(dict)
        self.sideBar: dict = dict()

    @staticmethod
    def create():
        gb = GridOptionsBuilder()
        return gb

    def configure_index(self, index_field : str):
        self.configure_grid_options(index=index_field)

    def configure_default_column(self, column_width=90, resizable=True, filterable=True, sortable=True, editable=False, groupable=False, sorteable=None, **other_default_column_properties):
        """Configure default column.

        Args:
            column_width (int, optional):
                column width. Defaults to 100.

            resizable (bool, optional):
                All columns will be resizable. Defaults to True.

            filterable (bool, optional):
                All columns will be filterable. Defaults to True.

            sortable (bool, optional):
                All columns will be sortable. Defaults to True.

            sorteable (bool, optional):
                Backwards compatibility alias for sortable. Overrides sortable if not None.

            groupable (bool, optional):
                All columns will be groupable based on row values. Defaults to True.

            editable (bool, optional):
                All columns will be editable. Defaults to True.

            groupable (bool, optional):
                All columns will be groupable. Defaults to True.

            **other_default_column_properties:
                Key value pairs that will be merged to defaultColDef dict.
                Chech ag-grid documentation.
        """
        if sorteable is not None:
            sortable = sorteable

        defaultColDef = {
            "width": column_width,
            "editable": editable,
            "filter": filterable,
            "resizable": resizable,
            "sortable": sortable,
        }
        if groupable:
            defaultColDef["enableRowGroup"] = groupable

        if other_default_column_properties:
            defaultColDef = {**defaultColDef, **other_default_column_properties}

        self.__grid_options["defaultColDef"] = defaultColDef
    
    def configure_column(self, field,  other_column_properties =None,header_name=None):
        """Configures an individual column
        check https://www.ag-grid.com/javascript-grid-column-properties/ for more information.

        Args:
            field (String): field name, usually equals the column header.
            header_name (String, optional): [description]. Defaults to None.
        """
        if not self.__grid_options.get("columnDefs", None):
            self.__grid_options["columnDefs"] = defaultdict(dict)

        colDef = {"headerName": field if header_name is None else header_name, "field": field}

        if other_column_properties:
            colDef = {**colDef, **other_column_properties}

        self.__grid_options["columnDefs"][field].update(colDef)
    
    def configure_grid_options(self, **props):
        """Merges props to gridOptions

        Args:
            props (dict): props dicts will be merged to gridOptions root.
        """
        self.__grid_options.update(props)
        
    def build(self):
        self.__grid_options["columnDefs"] = list(self.__grid_options["columnDefs"].values())
        return self.__grid_options