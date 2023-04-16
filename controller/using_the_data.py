from flask import Blueprint, render_template, request, flash
from controller.controller_helper import (
    get_controller_general_template_with_args,
    get_controller_filename,
    get_all_datasets,
    get_active_dataframe,
    generate_h2o_model,
    get_all_ml_models,
    download_file,
    get_model_statistics
)
import unicodedata

using_the_data = Blueprint(
    "using_the_data",
    __name__,
    static_folder="static",
    template_folder="../templates/using_the_data/",
)

method_usage_list = [
    "output_to_file",
    "h2o_automl",
    "model_insights",
    "make_predictions",
]


def get_controller_specific_template_with_args(
    template_name_arg="index_using_the_data.html",
    sub_navbar_active_arg="",
    *additional_args
):
    return get_controller_general_template_with_args(
        template_name_arg,
        method_usage_list,
        sub_navbar_active_arg,
        get_controller_filename(__name__),
        *additional_args
    )


@using_the_data.route("/")
@using_the_data.route("/home")
def home():
    return get_controller_specific_template_with_args("index_using_the_data.html")


@using_the_data.route("/h2o_automl", methods=["POST", "GET"])
def h2o_automl():
    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            if (
                "submit_predict_using_h2o" in request.form
                and "column_to_predict" in request.form
                and request.form["column_to_predict"] != "None"
            ):
                # print(request.form["column_to_predict"])
                print(generate_h2o_model(request.form["column_to_predict"]))
            else:
                flash(
                    "Please choose a dataset and a column to predict to use this functionality",
                    "info",
                )

        return get_controller_specific_template_with_args(
            "h2o_automl.html", h2o_automl.__name__, get_active_dataframe()
        )
    else:
        return "Use get or post to request this page"


@using_the_data.route("/output_to_file", methods=["POST", "GET"])
def output_to_file():
    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            if (
                "submit_export_file" in request.form
                and "file_to_export" in request.form
                and request.form["file_to_export"] != "None"
            ):
                return download_file(request.form["file_to_export"], "dataset")
                # print(request.form["file_to_export"])
            elif (
                "submit_ml_model_to_export" in request.form
                and "ml_model_to_export" in request.form
                and request.form["ml_model_to_export"] != "None"
            ):
                # print(request.form["ml_model_to_export"])
                return download_file(request.form["ml_model_to_export"], "ml_model")
            else:
                flash(
                    "Please choose a file or machine learning model.",
                    "info",
                )

        return get_controller_specific_template_with_args(
            "output_to_file.html",
            output_to_file.__name__,
            get_all_datasets(),
            get_all_ml_models(),
        )
    else:
        return "Use get or post to request this page"


@using_the_data.route("/make_predictions", methods=["POST", "GET"])
def make_predictions():
    if request.method == "GET" or request.method == "POST":
        if request.method == "POST":
            print("nothing")
            # if (
            #     "submit_predict_using_h2o" in request.form
            #     and "column_to_predict" in request.form
            #     and request.form["column_to_predict"] != "None"
            # ):
            #     # print(request.form["column_to_predict"])
            #     print(generate_h2o_model(request.form["column_to_predict"]))
            # else:
            #     flash(
            #         "Please choose a dataset and a column to predict to use this functionality",
            #         "info",
            #     )

        return get_controller_specific_template_with_args(
            "make_predictions.html", make_predictions.__name__, get_all_ml_models()
        )
    else:
        return "Use get or post to request this page"


@using_the_data.route("/model_insights", methods=["POST", "GET"])
def model_insights():
    if request.method == "GET" or request.method == "POST":
        model_type = ""
        output = ""
        if request.method == "POST":
            if (
                "submit_ml_model_for_statistics" in request.form
                and "ml_model_for_statistics" in request.form
                and request.form["ml_model_for_statistics"] != "None"
            ):
                model_statistics, confusion_matrix = get_model_statistics(request.form["ml_model_for_statistics"])

                # print(type(model_statistics))
                # print(model_statistics)

                if model_statistics["model_category"] == "Regression":
                    model_type = "regression"
                    # print("regression. MAE: ")
                    # print(model_statistics["mae"])
                    output = [model_statistics["MSE"], model_statistics["mae"], model_statistics["r2"]]
                elif model_statistics["model_category"] == "Multinomial":
                    model_type = "multinomial"
                    # # print(confusion_matrix)
                    # # print(type(confusion_matrix))

                    # object_methods = [method_name for method_name in dir(confusion_matrix)
                    #               if callable(getattr(confusion_matrix, method_name))]
                    # print("")
                    # print("")
                    # print("")
                    # print(object_methods)
                    # print("")
                    # print("")
                    # print("")
                    # print(model_statistics["model_category"])
                    # print(confusion_matrix.as_data_frame())


                    confusion_matrix_df = confusion_matrix.as_data_frame()
                    # print(confusion_matrix_df.transpose().reset_index())

                    # print(confusion_matrix_df)
                    first_col = confusion_matrix_df.transpose().reset_index()["index"].tolist()
                    first_col.remove("Error")
                    first_col.remove("Rate")
                    first_col.append("Sum")
                    confusion_matrix_df.insert(loc=0, column="-", value=first_col)


                    last_row_column_value = confusion_matrix_df['Rate'].values[-1]

                    print(last_row_column_value)
                    total_errors = unicodedata.normalize("NFKD", last_row_column_value.split("/")[0]).replace(" ", "").strip()
                    total_evaluations = unicodedata.normalize("NFKD", last_row_column_value.split("/")[1]).replace(" ", "").strip()
                    print(total_errors)
                    print(total_evaluations)

                    output = [confusion_matrix_df.to_dict("records"), (1 - (float(total_errors) / float(total_evaluations))) * 100]

                elif model_statistics["model_category"] == "Binomial":
                    model_type = "binomial"
                    output = confusion_matrix.to_html()
                else: 
                    flash("Model category of the trained model not currently supported nicely.", "info")
                    flash(str(model_statistics), "info")

                # print(request.form["file_to_export"])
            else:
                flash(
                    "Please choose a machine learning model.",
                    "info",
                )

        return get_controller_specific_template_with_args(
            "model_insights.html",
            model_insights.__name__,
            output, model_type, get_all_ml_models()
        )
    else:
        return "Use get or post to request this page"
