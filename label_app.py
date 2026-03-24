import dash
from dash import dash_table, dcc, html, Input, Output, callback, State
from dash.exceptions import PreventUpdate
import pandas as pd
import dash_ag_grid as dag
import pickle
import os

def eval_label_seq(timings, labels):
    if not("diagnosis" in labels):
        return "No_Label", "No_Label"
    t_diag = timings[labels.index("diagnosis")]
    valids = [(t, l) for t,l in zip(timings, labels) if t_diag-48 <= t < t_diag]
    if not(valids):
        return t_diag, t_diag
    t_valid, l_valid = zip(*valids)
    if "suspicion" in l_valid:
        index_onset = len(l_valid) - l_valid[::-1].index("suspicion") - 1
        t_onset = t_valid[index_onset]
        return t_diag, t_onset
    if "cause" in l_valid:
        index_onset = len(l_valid) - l_valid[::-1].index("cause") - 1
        t_onset = t_valid[index_onset]
        return t_diag, t_onset
    return t_diag, t_diag

def prepare_data(file):
    df = pd.read_csv(file, index_col=0)
    df["doc_an"] = ""
    return df.to_dict('records')

def prepare_patient(file):
    with open(file, 'rb') as file:
        assigenment = pickle.load(file)
    return assigenment


def compute_diag_and_onset(df):
    records = df.to_dict("records")
    ai_diag, ai_onset, = eval_label_seq(df["hour"].tolist(), df["ai"].tolist())
    human_1_diag, human_1_onset = eval_label_seq(df["hour"].tolist(), df["human_1"].tolist())
    human_2_diag, human_2_onset = eval_label_seq(df["hour"].tolist(), df["human_2"].tolist())
    new_df = []
    for r in records:
        r_new = r.copy()
        for diag, onset, name in zip([ai_diag, human_1_diag, human_2_diag],[ai_onset, human_1_onset, human_2_onset],["ai", "h1", "h2"]):
            if r["hour"] == diag:
                r_new.update({f"c_{name}":"red"})
            elif r["hour"] == onset:
                r_new.update({f"c_{name}":"yellow"})
            else:
                r_new.update({f"c_{name}":""})
        new_df.append(r_new)
    return pd.DataFrame(new_df)


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Input(
            id="user_name",
            type="text",
            placeholder="input name",
        ),
        dcc.Button('Submit Name', id='submit_name', n_clicks=0),
    ],id="login_part", hidden=False),
    html.Div([
            html.Div(
            "Count Patient 1/300",
            id="annoation_counter",
            style={"color": "black", "font-weight": "bold"},
        ),
        dag.AgGrid(
            id='table-dropdown',
            columnDefs=[
                    {
                    "field": "sent",
                    "headerName": "Text",
                    "editable": False,
                    "flex": 4,
                    "minWidth": 1000,
                    "wrapText": True,
                    "autoHeight": True,
                    "cellStyle": {
                        "whiteSpace": "pre-line",
                        "lineHeight": "1.6",
                        "padding": "8px",
                    },
                },
                {"field": "hour",    "headerName": "Hour",      "editable": False, "minWidth": 80},
                {"field": "human_1", "headerName": "Human 1", "editable": False, "minWidth": 80,
                    "cellStyle": {"styleConditions": [
                        {"condition": "params.data.c_h1 === 'yellow'", "style": {"backgroundColor": "#FFF3CD"}},
                        {"condition": "params.data.c_h1 === 'red' && params.data.human_1 === 'diagnosis'",    "style": {"backgroundColor": "#FFCCCC"}}
                    ]}
                },
                {"field": "human_2", "headerName": "Human 2", "editable": False, "minWidth": 80,
                    "cellStyle": {"styleConditions": [
                        {"condition": "params.data.c_h2 === 'yellow'", "style": {"backgroundColor": "#FFF3CD"}},
                        {"condition": "params.data.c_h2 === 'red' && params.data.human_2 === 'diagnosis'",    "style": {"backgroundColor": "#FFCCCC"}}
                    ]}
                },
                {"field": "ai", "headerName": "Ai", "editable": False, "minWidth": 80,
                    "cellStyle": {"styleConditions": [
                        {"condition": "params.data.c_ai === 'yellow'", "style": {"backgroundColor": "#FFF3CD"}},
                        {"condition": "params.data.c_ai === 'red' && params.data.ai === 'diagnosis'",    "style": {"backgroundColor": "#FFCCCC"}}
                    ]}
                },
                {
                    "field": "doc_an",
                    "headerName": "Annotations",
                    "editable": True,
                    "width": 130,
                    "cellEditor": "agSelectCellEditor",
                    "cellEditorParams": {
                        "values": ["", "onset", "diagnosis"]
                    },
                },
            ],
            rowData=[],
            defaultColDef={
                "resizable": True,
                "wrapText": True,
                "autoHeight": True,
            },
            columnSize="responsiveSizeToFit", 
            style={"height": "800px", "width": "100%"},
            className="ag-theme-alpine",
            dashGridOptions={
                "singleClickEdit": True,
                "rowHeight": None,
                "headerHeight": 40,
                "suppressVirtualisation": True,
                "rowBuffer": 100,
            },
        ),
        dcc.Button('Submit', id='submit', n_clicks=0)
    ], id="label_part", hidden=True),
    dcc.Store("annoation_data", data=prepare_data("reannotation_r2.csv")),
    dcc.Store("patients_todo"),
    dcc.Store("patient_assigment", data=prepare_patient("assigenment_r2_r.pkl")),
    dcc.Store("label_results", data=[]),
    dcc.Store("table_mem", data=[])
])


@callback(
    Output('table-dropdown', 'rowData', allow_duplicate=True),
    Output("table_mem", "data", allow_duplicate=True),
    Input("table-dropdown", "cellValueChanged"),
    State("table-dropdown", "rowData"),
    State("table_mem", "data"),
    prevent_initial_call='initial_duplicate'
)
def specific_table_updates(change, annoation, table_save):
    if not(annoation) or change is None:
        raise PreventUpdate
    annoation_df = pd.DataFrame(annoation)
    no_diagnosis = annoation_df[annoation_df["doc_an"] == "diagnosis"].empty
    if table_save:
        table_save = pd.DataFrame(table_save)
        match_cols = [col for col in annoation_df.columns if col != "doc_an"]
        table_save["_key"] = pd.util.hash_pandas_object(table_save[match_cols], index=False)
        annoation_df["_key"] = pd.util.hash_pandas_object(annoation_df[match_cols], index=False)
        key_to_doc_an = annoation_df.set_index("_key")["doc_an"]
        mask = table_save["_key"].isin(key_to_doc_an.index)
        table_save.loc[mask, "doc_an"] = table_save.loc[mask, "_key"].map(key_to_doc_an)
        table_save = table_save.drop(columns=["_key"])
        if no_diagnosis:
            return table_save.to_dict("records"), table_save.to_dict("records")
        else:
            diag_hour = table_save[table_save["doc_an"] == "diagnosis"]["hour"].tolist()[0]
            subset_df = table_save[[True if diag_hour-48 <=hour <= diag_hour else False for hour in table_save["hour"]]]
            return subset_df.to_dict("records"), table_save.to_dict("records")
    else:
        if not(no_diagnosis):
            diag_hour = annoation_df[annoation_df["doc_an"] == "diagnosis"]["hour"].tolist()[0]
            subset_df = annoation_df[[True if diag_hour-48 <=hour <= diag_hour else False for hour in annoation_df["hour"]]]
            return subset_df.to_dict("records"), annoation_df.to_dict("records")
        else:
            raise PreventUpdate


@callback(
    Output('table-dropdown', 'rowData', allow_duplicate=True),
    Output("patients_todo", "data", allow_duplicate=True),
    Output("label_part", "hidden"),
    Output("login_part", "hidden"),
    Output("annoation_counter", "children", allow_duplicate=True),
    Output("label_results", "data", allow_duplicate=True),
    Output("table_mem", "data", allow_duplicate=True),
    Input('submit_name', "n_clicks"),
    State("user_name", "value"),
    State("annoation_data", "data"),
    State("patient_assigment", "data"),
    prevent_initial_call='initial_duplicate'
)
def init_annoation_data(n_clicks, name, annotation_data, assignement):
    if not(name in assignement.keys()):
        raise PreventUpdate
    assignement = assignement[name]
    max_patient = len(assignement)
    done = 0
    annoation_results = []
    if os.path.exists("results/"+ name + ".csv"):
        annoation_results = pd.read_csv("results/"+ name + ".csv", index_col=0)
        patients_done = annoation_results["ts_id"].unique()
        assignement = [a for a in assignement if not(a in patients_done)]
        done = len(patients_done)
        annoation_results = annoation_results.to_dict("records")
    first_key = assignement.pop()
    df = pd.DataFrame(annotation_data)
    df_out = df[df["ts_id"] == first_key].sort_values(by=["hour"])
    df_out = compute_diag_and_onset(df_out)
    text = f"Patient {done}/{max_patient}"
    return df_out.to_dict('records'), assignement, False, True, text, annoation_results, df_out.to_dict('records')

@callback(
    Output('table-dropdown', 'rowData', allow_duplicate=True),
    Output("patients_todo", "data", allow_duplicate=True),
    Output("annoation_counter", "children", allow_duplicate=True),
    Output("table_mem", "data", allow_duplicate=True),
    Input('submit', "n_clicks"),
    State("user_name", "value"),
    State("annoation_data", "data"),
    State("patients_todo", "data"),
    State("patient_assigment", "data"),
    State('table-dropdown', 'rowData'),
    prevent_initial_call='initial_duplicate'
)
def plot_patient_data(n_clicks, name, annotation_data, todo, assignement, annoation):
    if n_clicks == 0:
        raise PreventUpdate
    annoation_df = pd.DataFrame(annoation)
    hours = annoation_df["hour"].tolist()
    labels =  annoation_df["doc_an"].tolist()
    onset_times = [(t, l) for t, l in zip(hours, labels) if l == "onset"]
    diag_times = [(t, l) for t, l in zip(hours, labels) if l == "diagnosis"]
    if (len(diag_times) == 0 and len(onset_times) == 0) or (len(diag_times) == 1 and len(onset_times) == 0) or (len(diag_times) == 1 and len(onset_times) == 1 and diag_times[0][0]-48 <= onset_times[0][0] <= diag_times[0][0]):
        max_patient = len(assignement[name])
        done = max_patient - len(todo) 
        first_key = todo.pop()
        df = pd.DataFrame(annotation_data)
        df_out = df[df["ts_id"] == first_key].sort_values(by=["hour"])
        df_out = compute_diag_and_onset(df_out)
        text = f"Patient {done}/{max_patient}"
        return df_out.to_dict('records'), todo, text, df_out.to_dict('records')
    else:
        raise PreventUpdate

@callback(
    Output("label_results", "data", allow_duplicate=True),
    Input('submit', "n_clicks"),
    State("user_name", "value"),
    State('table-dropdown', 'rowData'),
    State("label_results", "data"),
    prevent_initial_call='initial_duplicate'
)
def save_annoation(n_clicks, user_name, annoation, all_annoations):
    if n_clicks == 0:
        raise PreventUpdate
    annoation_df = pd.DataFrame(annoation)
    hours = annoation_df["hour"].tolist()
    labels =  annoation_df["doc_an"].tolist()
    onset_times = [(t, l) for t, l in zip(hours, labels) if l == "onset"]
    diag_times = [(t, l) for t, l in zip(hours, labels) if l == "diagnosis"]
    if len(diag_times) == 0 and len(onset_times) == 0:
        new_data = {"ts_id":annoation_df["ts_id"].tolist()[0], "onset":"no_sepsis", "diagnosis":"no_sepsis"}
        all_annoations.append(new_data)
        pd.DataFrame(all_annoations).to_csv(f"results/{user_name}.csv")
        return all_annoations
    elif len(diag_times) == 1 and len(onset_times) == 0:
        new_data = {"ts_id":annoation_df["ts_id"].tolist()[0], "onset":diag_times[0][0], "diagnosis":diag_times[0][0]}
        all_annoations.append(new_data)
        pd.DataFrame(all_annoations).to_csv(f"results/{user_name}.csv")
        return all_annoations
    elif len(diag_times) == 1 and len(onset_times) == 1 and diag_times[0][0]-48 <= onset_times[0][0] <= diag_times[0][0]:
        onset = onset_times[0][0] if onset_times else diag_times[0][0]
        new_data = {"ts_id":annoation_df["ts_id"].tolist()[0], "onset":onset, "diagnosis":diag_times[0][0]}
        all_annoations.append(new_data)
        pd.DataFrame(all_annoations).to_csv(f"results/{user_name}.csv")
        return all_annoations
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run(debug=True)