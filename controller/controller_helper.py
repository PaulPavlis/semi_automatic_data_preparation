from flask import render_template, current_app, redirect, url_for, flash, send_file
import os
import pandas as pd
import yaml
import shutil

from AutoClean import AutoClean

import h2o
from h2o.automl import H2OAutoML


def get_controller_general_template_with_args(
    template_name="index.html",
    sub_navbar_list_arg=None,
    sub_navbar_active_arg="",
    main_navbar_active_arg="",
    *additional_args,
):
    return render_template(
        template_name,
        sub_navbar_list=sub_navbar_list_arg,
        sub_navbar_active=sub_navbar_active_arg,
        main_navbar_active=main_navbar_active_arg,
        active_dataset_info=f"Currently active dataset: {get_active_dataset_name()} || Infos: {get_dataset_basic_info_string(get_active_dataframe())}"
        if get_active_dataset_name()
        else "No active dataframe selected. Please choose one under data_selection --> select_dataset_as_active",
        additional_args=additional_args,
    )


def get_all_datasets():
    return [
        f
        for f in os.listdir(current_app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["UPLOAD_FOLDER"], f))
    ]


def get_all_ml_models():
    return [
        f
        for f in os.listdir(current_app.config["STORED_ML_MODELS_FOLDER"])
        if os.path.isfile(
            os.path.join(current_app.config["STORED_ML_MODELS_FOLDER"], f)
        )
    ]


def get_active_dataset_list():
    return [
        f
        for f in os.listdir(current_app.config["ACTIVE_DATASET_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], f))
    ]


def set_active_file(new_active_dataset_name, omit_flash_message=False):
    active_dataset_list = get_active_dataset_list()

    for active_dataset in active_dataset_list:
        shutil.move(
            os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], active_dataset),
            os.path.join(current_app.config["UPLOAD_FOLDER"], active_dataset),
        )

    # Move new active dataset to active folder
    if new_active_dataset_name:
        shutil.copyfile(
            os.path.join(current_app.config["UPLOAD_FOLDER"], new_active_dataset_name),
            os.path.join(
                current_app.config["ACTIVE_DATASET_FOLDER"], new_active_dataset_name
            ),
        )

    if not omit_flash_message:
        flash(
            f"Successfully set {new_active_dataset_name} as the active dataset.",
            "success",
        )


def get_active_dataset_name():
    # Only get the first one (should also only ever be one)
    active_datasets = [
        f
        for f in os.listdir(current_app.config["ACTIVE_DATASET_FOLDER"])
        if os.path.isfile(os.path.join(current_app.config["ACTIVE_DATASET_FOLDER"], f))
    ]

    return active_datasets[0] if active_datasets else None


def get_active_dataframe(reset_index=True):
    if not get_active_dataset_name():
        return pd.DataFrame()
    return read_generic_input_file(
        current_app.config["ACTIVE_DATASET_FOLDER"],
        get_active_dataset_name(),
        reset_index,
    )


def get_active_dataframe_formatted():
    return get_active_dataframe().to_dict("records")


def get_active_dataframe_prepared_formatted():
    return get_active_dataframe_prepared().to_dict("records")


def get_dataset_basic_info_string(dataframe):
    if dataframe.empty:
        return "No dataframe given."
    return (
        f"Number of rows: {dataframe.shape[0]}, Number of columns: {dataframe.shape[1]}"
    )


def read_generic_input_file(file_location, file_name, reset_index=True):
    if not file_name:
        return pd.DataFrame()
    file_extension = get_file_extension(file_name)
    file_path = os.path.join(file_location, file_name)

    pd_read_function = None

    if file_extension == "csv":
        pd_read_function = pd.read_csv
    elif file_extension == "json":
        pd_read_function = pd.read_json
    else:
        flash("This file extension is currently not supported.", "danger")
        return None

    user_file_configs = get_user_file_config(file_name)

    header_value = None
    file_separator = ","
    index_value = None
    column_types = {}
    na_value_list = []
    if user_file_configs:
        header_value = (
            0
            if "has_header" in user_file_configs
            and user_file_configs["has_header"]["value"]
            else None
        )
        file_separator = (
            user_file_configs["file_separator"]["value"]
            if "file_separator" in user_file_configs
            else ","
        )
        index_value = (
            0
            if "has_index" in user_file_configs
            and user_file_configs["has_index"]["value"]
            else None
        )
        column_types = (
            user_file_configs["column_types"]
            if "column_types" in user_file_configs and user_file_configs["column_types"]
            else {}
        )
        na_value_list = (
            user_file_configs["na_values_list"]
            if "na_values_list" in user_file_configs
            and user_file_configs["na_values_list"]
            else []
        )

    try:
        if not column_types:
            df = pd_read(
                file_path,
                header_value,
                file_separator,
                index_value,
                reset_index,
                pd_read_function,
                {},
                na_value_list,
            )
            # print(df)
            # print(df.dtypes)
            # print(df.dtypes.to_dict())
            if user_file_configs:
                column_types = df.dtypes.to_dict()
                # print(f"{column_types=}")
                for key, value in column_types.items():
                    column_types[key] = str(value)
                # print(f"{column_types=}")
                user_file_configs["column_types"] = column_types
                create_or_modify_user_config_file(
                    file_name,
                    create_config_dict(
                        user_file_configs["has_header"]["value"],
                        user_file_configs["file_separator"]["value"],
                        user_file_configs["has_index"]["value"],
                        user_file_configs["column_types"],
                    ),
                )

            # print(df.dtypes.reset_index().to_dict())
            # return None

        df = pd_read(
            file_path,
            header_value,
            file_separator,
            index_value,
            reset_index,
            pd_read_function,
            column_types=column_types,
            na_value_list=na_value_list,
        )

        # print(f"{df.dtypes=}")

        return df
    except Exception as e:
        print(
            f"Got exception reading generic input file. Printing variables: \n{pd_read_function=}, {header_value=}, {file_separator=} {user_file_configs=}",
            "warning",
        )
        print(f"Error message: {e}")
        flash(
            f"It seems like the configs of the active file are not suitable to read the file. Config values are: {header_value=} | {file_separator=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")
        return pd.DataFrame()


def pd_read(
    file_path,
    header_value,
    file_separator,
    index_value,
    reset_index,
    pd_read_function,
    column_types={},
    na_value_list=[],
):
    datetime_column_list = []

    for key, value in column_types.items():
        if value == "datetime64":
            datetime_column_list.append(key)

    for entry in datetime_column_list:
        column_types.pop(entry)

    df = pd_read_function(
        file_path,
        encoding="latin1",
        header=header_value,
        sep=file_separator,
        index_col=index_value,
        dtype=column_types,
        na_values=na_value_list,
        keep_default_na=True,
        parse_dates=datetime_column_list,
        dayfirst=True,
    )

    df.columns = df.columns.astype(
        str
    )  # otherwise weird errors if columns are named with just numbers

    df = df.rename(
        columns=lambda x: x.lstrip()
    )  # Remove whitespaces before and after the column names
    df = df.rename(
        columns=lambda x: x.rstrip()
    )  # Remove whitespaces before and after the column names

    # print(df)
    if reset_index:
        df = df.reset_index()  # to show the index value
        if index_value == None:
            df.rename(columns={"index": "generated_index"}, inplace=True)
        # else:
        #     df = df.reset_index()  # to show the index value
        # print("------------")

    # print(df)

    return df


def get_controller_filename(complete_name):
    return complete_name.split(".")[1]


def is_allowed_file(filename):
    return (
        "." in filename
        and get_file_extension(filename) in current_app.config["ALLOWED_EXTENSIONS"]
    )


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def get_filename_without_extension(filename):
    return filename.rsplit(".", 1)[0].lower()


def check_if_active_dataset_is_set():
    return True if get_active_dataset_name() else False


def send_user_to_set_active_dataset():
    flash("You need to select an active dataset first. Redirecting you ...", "warning")
    return redirect(url_for("data_selection.select_dataset_as_active"))


def get_user_file_config_name(user_file_name):
    return f"{str(get_filename_without_extension(user_file_name))}.yaml"


def get_active_user_file_config():
    return get_user_file_config(get_active_dataset_name())


def create_user_file_config(user_file_name, config_dict={}):
    if not isinstance(config_dict, dict):
        return None

    with open(
        os.path.join(
            current_app.config["USER_FILE_CONFIGS"],
            get_user_file_config_name(user_file_name),
        ),
        "w+",
    ) as fw:
        yaml.dump(config_dict, fw, default_flow_style=False, allow_unicode=True)
        flash("User file config adaptations were successful.", "success")


def get_user_file_config(user_file_name):
    user_file_config_full_path = os.path.join(
        current_app.config["USER_FILE_CONFIGS"],
        get_user_file_config_name(user_file_name),
    )

    if not os.path.exists(user_file_config_full_path):
        create_user_file_config(
            user_file_name,
            create_config_dict(),
        )
        flash("No persisted user file configs found. Creating it for you.", "info")

    with open(user_file_config_full_path, "r") as fr:
        try:
            return yaml.safe_load(fr)
        except yaml.YAMLError as exc:
            print(exc)


def create_or_modify_user_config_file(user_file_name, config_dict={}):
    if not isinstance(config_dict, dict):
        return None

    current_configs = get_user_file_config(get_user_file_config_name(user_file_name))

    # print(f"{current_configs=}")
    # print(f"{config_dict=}")

    if not current_configs:
        flash("No persisted user file configs found. Creating it for you.", "info")
        current_configs = config_dict
    else:
        current_configs.update(config_dict)

    # print(f"Updated dict: {current_configs}")

    final_configs = {
        config_option: config_dict[config_option]
        for config_option in current_app.config["USER_FILE_CONFIGS_OPTIONS"]
        if config_option in config_dict
    }

    # print(f"Updated dict after checking options: {final_configs}")

    create_user_file_config(get_user_file_config_name(user_file_name), final_configs)


def create_config_dict(
    has_header=False,
    file_separator=",",
    has_index=False,
    column_types={},
    na_values_list=[],
):
    user_file_configs = {
        "has_header": {
            "bootstrap_input_type": "checkbox",
            "bootstrap_class": "form-check-input",
        },
        "file_separator": {"bootstrap_input_type": "text", "bootstrap_class": ""},
        "has_index": {
            "bootstrap_input_type": "checkbox",
            "bootstrap_class": "form-check-input",
        },
        "column_types": column_types,
        "na_values_list": na_values_list,
    }

    user_file_configs["has_header"]["value"] = True if has_header else False

    user_file_configs["file_separator"]["value"] = (
        file_separator if file_separator else ","
    )

    user_file_configs["has_index"]["value"] = True if has_index else False

    # This is so that the types are nullables
    if "column_types" in user_file_configs:
        # print(user_file_configs["column_types"])
        for key, value in user_file_configs["column_types"].items():
            if not str(value).find("int"):
                user_file_configs["column_types"][key] = str(value).replace(
                    "int", "Int"
                )
            if not str(value).find("float"):
                user_file_configs["column_types"][key] = str(value).replace(
                    "float", "Float"
                )
            # print(user_file_configs["column_types"])

    # print(user_file_configs["column_types"])
    return user_file_configs


def return_empty_plot(display_text="No data selected"):
    return {
        "layout": {
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": display_text,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 28},
                }
            ],
        }
    }


def create_or_modify_file(new_prepared_df=pd.DataFrame(), file_path="", file_name=""):
    if new_prepared_df.empty:
        return None

    user_file_configs = get_active_user_file_config()

    new_prepared_df.to_csv(
        os.path.join(
            file_path,
            file_name,
        ),
        encoding="latin1",
        index=False,
        sep=user_file_configs["file_separator"]["value"],
        header=user_file_configs["has_header"]["value"],
    )


def create_or_modify_active_prepared_file(new_prepared_df=pd.DataFrame()):
    delete_all_prepared_files()

    create_or_modify_file(
        new_prepared_df,
        current_app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"],
        get_active_dataset_name(),
    )
    # flash("Prepared file was saved successfully.", "success")


def create_or_modify_active_file(new_prepared_df=pd.DataFrame()):
    create_or_modify_file(
        new_prepared_df,
        current_app.config["ACTIVE_DATASET_FOLDER"],
        get_active_dataset_name(),
    )
    delete_all_prepared_files()
    flash("Active file was saved successfully.", "success")


def get_active_dataframe_prepared(reset_index=True):
    if not get_active_dataset_prepared_name():
        return pd.DataFrame()
    return read_generic_input_file(
        current_app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"],
        get_active_dataset_prepared_name(),
        reset_index,
    )


def get_active_dataset_prepared_name():
    active_datasets_prepared = [
        f
        for f in os.listdir(current_app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"])
        if os.path.isfile(
            os.path.join(current_app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"], f)
        )
    ]

    return active_datasets_prepared[0] if active_datasets_prepared else None


# This function consists of spaghetti code. I cannot be bother to rewrite it again for a poc
def add_row_to_active_df(add_row_dict):
    active_df = get_active_dataframe(reset_index=False)
    index_name = active_df.index.name if active_df.index.name else "generated_index"
    new_row = {}
    new_row_list = []
    for column in active_df.columns:
        if column in add_row_dict:
            new_row_list.append(add_row_dict[column])
            new_row[column] = add_row_dict[column]
            # print(f"{column}={add_row_dict[column]}")

    if get_active_user_file_config()["has_index"]["value"] == True:
        if not add_row_dict[index_name]:
            flash(
                f"Please specify the index variable to add to the df ({index_name}).",
                "warning",
            )
            return None
        new_row[index_name] = add_row_dict[index_name]
        active_df = active_df.reset_index()

    # print(active_df)
    new_row_list = []
    new_row_list.insert(0, new_row)
    df_prepared = pd.concat([pd.DataFrame(new_row_list), active_df], ignore_index=True)

    # print(new_row_list)
    # print(active_df)
    # print(df_prepared)

    if get_active_user_file_config()["has_index"]["value"] == True:
        df_prepared = df_prepared.set_index(index_name).reset_index()
        # print(df_prepared)
    # else:
    #     df_prepared = df_prepared.set_index("generated_index")
    # new_row_list.insert(0, new_row)
    # df_prepared = pd.concat(
    #     [pd.DataFrame(new_row_list), active_df], ignore_index=True
    # )

    # print(df_prepared)

    create_or_modify_active_file(df_prepared)

    flash("Added row to df successfully", "success")
    return None


def remove_row_from_active_df(row_number):
    try:
        df_prepared = get_active_dataframe(reset_index=False).drop(
            index=[int(row_number)], axis=0
        )
        if get_active_user_file_config()["has_index"]["value"] == True:
            df_prepared = df_prepared.reset_index()
        create_or_modify_active_file(df_prepared)
        flash("Removed row from df successfully", "success")
        return None
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like you are trying to delete a row with an index that does not exist: {row_number=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")


def remove_column_from_active_df(column_name):
    try:
        df_prepared = get_active_dataframe(reset_index=False).drop(
            [column_name], axis=1
        )
        if get_active_user_file_config()["has_index"]["value"] == True:
            df_prepared = df_prepared.reset_index()
        create_or_modify_active_file(df_prepared)
        flash("Removed row from df successfully", "success")
        return None
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like you are trying to delete a column with a name that does not exist: {column_name=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")


def delete_all_prepared_files():
    prepared_dataset_list = get_prepared_dataset_list()

    for prepared_dataset in prepared_dataset_list:
        os.remove(
            os.path.join(
                current_app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"],
                prepared_dataset,
            )
        )


def get_prepared_dataset_list():
    return [
        f
        for f in os.listdir(current_app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"])
        if os.path.isfile(
            os.path.join(current_app.config["ACTIVE_DATASET_TRANSFORMED_FOLDER"], f)
        )
    ]


def change_column_type(column_name, new_column_type):
    try:
        # print(get_active_dataframe(reset_index=False).dtypes)
        # df_prepared = get_active_dataframe(reset_index=False).astype(
        #     {column_name: new_column_type}
        # )
        # print(df_prepared.dtypes)

        config_dict = get_active_user_file_config()
        config_dict["column_types"][column_name] = str(new_column_type)

        create_or_modify_user_config_file(get_active_dataset_name(), config_dict)

        # This is of no use since it gets read newly everytime. Must change configs.
        # create_or_modify_active_file(df_prepared)
        flash(
            f"Changed {column_name} type of df to {new_column_type} successfully",
            "success",
        )
        return None
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like you are trying to change a column type with a name or new_colum_type that does not exist: {column_name=} {new_column_type=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")


def change_column_name(column_name, new_column_name):
    try:
        # print(get_active_dataframe(reset_index=False).dtypes)
        # print(df_prepared.dtypes)

        config_dict = get_active_user_file_config()
        config_dict["column_types"][new_column_name] = config_dict["column_types"][
            column_name
        ]
        del config_dict["column_types"][column_name]
        create_or_modify_user_config_file(get_active_dataset_name(), config_dict)

        df_prepared = get_active_dataframe(reset_index=False).rename(
            columns={column_name: new_column_name}
        )
        if get_active_user_file_config()["has_index"]["value"] == True:
            df_prepared = df_prepared.reset_index()
        create_or_modify_active_file(df_prepared)

        flash(
            f"Changed {column_name} to {new_column_name} successfully",
            "success",
        )
        return None
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like you are trying to change a column name. This did not work correctly: {column_name=} {new_column_name=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")


def change_category_name(column_name, category_name, new_category_name):
    try:
        # print(get_active_dataframe(reset_index=False).dtypes)
        # print(df_prepared.dtypes)

        df_prepared = get_active_dataframe(reset_index=False)
        df_prepared[column_name] = df_prepared[column_name].cat.rename_categories(
            {category_name: new_category_name}
        )

        if get_active_user_file_config()["has_index"]["value"] == True:
            df_prepared = df_prepared.reset_index()
        create_or_modify_active_file(df_prepared)

        flash(
            f"Changed category {category_name} in {column_name} to {new_category_name} successfully",
            "success",
        )
        return None
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like you are trying to change the name of a category of column {column_name}. This did not work correctly: {column_name=} {category_name=} {new_category_name=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")


def get_active_dataframe_column_type(column_name):
    config_dict = get_user_file_config(get_active_dataset_name())
    if not "column_types" in config_dict:
        return "No column_types in config dictionary"
    if not column_name in config_dict["column_types"]:
        return "None"

    return config_dict["column_types"][column_name]


def get_active_dataframe_column_type_dict():
    config_dict = get_user_file_config(get_active_dataset_name())
    if not "column_types" in config_dict:
        return "No column_types in config dictionary"
    return config_dict["column_types"]


def filter_active_dataframe_string_column(
    prepare_column, match_string, has_to_be_complete_match, delete_matches, is_preview
):
    if prepare_column == "None":
        flash("No column selected.", "info")
        return

    active_df = get_active_dataframe(reset_index=False)
    df_prepared = pd.DataFrame()

    if has_to_be_complete_match:
        df_prepared = active_df[
            active_df[str(prepare_column)].str.contains(str(match_string))
            != delete_matches
        ]
    else:
        if delete_matches:
            df_prepared = active_df[
                ~active_df[str(prepare_column)].str.contains(
                    "|".join([str(match_string)])
                )
            ]
        else:
            df_prepared = active_df[
                active_df[str(prepare_column)].str.contains(
                    "|".join([str(match_string)])
                )
            ]

    # print(active_df)
    # print(df_prepared)

    if get_active_user_file_config()["has_index"]["value"] == True:
        df_prepared = df_prepared.reset_index()

    if is_preview:
        create_or_modify_active_prepared_file(df_prepared)
    else:
        create_or_modify_active_file(df_prepared)


def filter_active_dataframe_category_column(
    prepare_column, match_string, delete_matches, is_preview
):
    filter_active_dataframe_string_column(
        prepare_column, match_string, True, delete_matches, is_preview
    )


def handle_missing_values(
    handling_option, handle_numbers_received, handle_categories_received, is_preview
):
    active_df = get_active_dataframe(reset_index=False)
    handle_numbers = True
    handle_categories = True

    if handling_option == "delete":
        handle_numbers = "delete"
        handle_categories = "delete"
    elif handling_option == "substitute":
        handle_numbers = "mean"
        handle_categories = "most_frequent"
    elif handling_option == "predict":
        handle_numbers = "auto"
        handle_categories = "auto"
    elif handling_option == "impute":
        handle_numbers = "knn"
        handle_categories = "knn"

    if not handle_numbers_received:
        handle_numbers = False

    if not handle_categories_received:
        handle_categories = False

    # df_pipeline = AutoClean(
    #     active_df, mode="manual", missing_num="auto", missing_categ="auto", logfile=True
    # )
    df_pipeline = AutoClean(
        active_df,
        mode="manual",
        missing_num=handle_numbers,
        missing_categ=handle_categories,
        logfile=True,
    )

    df_prepared = df_pipeline.output
    # print(df_prepared)

    if get_active_user_file_config()["has_index"]["value"] == True:
        df_prepared = df_prepared.reset_index()

    if is_preview:
        create_or_modify_active_prepared_file(df_prepared)
    else:
        create_or_modify_active_file(df_prepared)


def add_na_value_type(new_na_value):
    config_dict = get_active_user_file_config()
    config_dict["na_values_list"].append(new_na_value)

    create_or_modify_user_config_file(get_active_dataset_name(), config_dict)

    # This is of no use since it gets read newly everytime. Must change configs.
    # create_or_modify_active_file(df_prepared)
    flash(
        f"Added new na value: {new_na_value} successfully",
        "success",
    )


def one_hot_encode_column(column_name, is_preview, remove_old_column):
    try:
        # print(get_active_dataframe(reset_index=False).dtypes)
        # print(df_prepared.dtypes)

        active_df = get_active_dataframe(reset_index=False)
        df_pipeline = AutoClean(
            active_df,
            mode="manual",
            encode_categ=["auto", [column_name]],
        )

        df_prepared = df_pipeline.output

        if get_active_user_file_config()["has_index"]["value"] == True:
            df_prepared = df_prepared.reset_index()

        config_dict = get_active_user_file_config()

        if remove_old_column:
            df_prepared = df_prepared.drop([column_name], axis=1)
            config_dict["column_types"].pop(column_name)

        for df_column_name in df_prepared:
            if column_name in df_column_name and column_name != df_column_name:
                config_dict["column_types"][df_column_name] = "Int64"

        if is_preview:
            create_or_modify_active_prepared_file(df_prepared)
        else:
            create_or_modify_active_file(df_prepared)
            # only change config file if it is permament
            create_or_modify_user_config_file(get_active_dataset_name(), config_dict)

        flash(
            f"Encoded column {column_name} successfully",
            "success",
        )
        return None
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like you are trying to encode column {column_name}. This did not work correctly: {column_name=} {is_preview=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")


def extract_dates_and_add(is_preview, remove_old_column):
    try:
        # print(get_active_dataframe(reset_index=False).dtypes)
        # print(df_prepared.dtypes)

        active_df = get_active_dataframe(reset_index=False)
        df_pipeline = AutoClean(
            active_df,
            mode="manual",
            extract_datetime="auto",
        )

        df_prepared = df_pipeline.output

        print(df_prepared)

        config_dict = get_active_user_file_config()

        # if remove_old_column:
        #     df_prepared = df_prepared.drop([column_name], axis=1)
        #     config_dict["column_types"].pop(column_name)

        for df_column_name in df_prepared:
            if df_column_name not in active_df:
                # print(df_column_name)
                config_dict["column_types"][df_column_name] = "Int64"

        if get_active_user_file_config()["has_index"]["value"] == True:
            df_prepared = df_prepared.reset_index()

        if is_preview:
            create_or_modify_active_prepared_file(df_prepared)
        else:
            create_or_modify_active_file(df_prepared)
            # only change config file if it is permament
            create_or_modify_user_config_file(get_active_dataset_name(), config_dict)

        flash(
            f"Extracted dates successfully",
            "success",
        )
        return None
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like you are trying to extract dates. This did not work correctly: {is_preview=}",
            "warning",
        )
        flash(f"Error message: {e}", "danger")


def remove_complete_duplicates(is_preview):
    active_df = get_active_dataframe(reset_index=False)

    df_pipeline = AutoClean(
        active_df,
        mode="manual",
        duplicates="auto",
    )

    df_prepared = df_pipeline.output
    # print(df_prepared)

    if get_active_user_file_config()["has_index"]["value"] == True:
        df_prepared = df_prepared.reset_index()

    if is_preview:
        create_or_modify_active_prepared_file(df_prepared)
        flash(
            f"Removed {active_df.shape[0] - df_prepared.shape[0]} duplicates (preview) succesfully.",
            "success",
        )
    else:
        create_or_modify_active_file(df_prepared)
        flash(
            f"Removed {active_df.shape[0] - df_prepared.shape[0]} duplicates succesfully.",
            "success",
        )


def return_automatically_removed_outliers_df():
    active_df = get_active_dataframe(reset_index=False)

    df_pipeline = AutoClean(
        active_df,
        mode="manual",
        outliers="auto",
    )

    df_prepared = df_pipeline.output
    # print(df_prepared)

    if get_active_user_file_config()["has_index"]["value"] == True:
        df_prepared = df_prepared.reset_index()

    return df_prepared


def automatically_prepare_active_df(
    is_preview,
    duplicates=True,
    missing_num=True,
    missing_categ=True,
    encode_categ=True,
    extract_datetime=True,
    outliers=True,
):
    df_prepared = get_active_dataframe(reset_index=False)

    if duplicates:
        df_prepared = return_df_AutoClean_duplicates(df_prepared, "auto")
    if outliers:
        df_prepared = return_df_AutoClean_outliers(df_prepared, "auto")
    if missing_categ:
        df_prepared = return_df_AutoClean_missing_categ(df_prepared, "auto")
    if encode_categ:
        df_prepared = return_df_AutoClean_encode_categ(df_prepared, "auto")
    if extract_datetime:
        df_prepared = return_df_AutoClean_extract_datetime(df_prepared, "auto")
    if missing_num:
        df_prepared = return_df_AutoClean_missing_num(df_prepared, "auto")

    if get_active_user_file_config()["has_index"]["value"] == True:
        df_prepared = df_prepared.reset_index()

    if is_preview:
        create_or_modify_active_prepared_file(df_prepared)
        flash(
            f"Automatically prepared df (preview) succesfully.",
            "success",
        )
    else:
        create_or_modify_active_file(df_prepared)
        flash(
            f"Automatically prepared df succesfully.",
            "success",
        )


def return_df_AutoClean(autoclean_pipeline):
    df_prepared = autoclean_pipeline.output

    if get_active_user_file_config()["has_index"]["value"] == True:
        # print(df_prepared)
        df_prepared = df_prepared.reset_index()
        df_prepared = df_prepared.set_index("index")

    return df_prepared


def return_df_AutoClean_duplicates(df, selected_mode):
    df_prepared = return_df_AutoClean(
        AutoClean(df, mode="manual", duplicates=selected_mode)
    )

    flash(
        f"Removed {df.shape[0] - df_prepared.shape[0]} duplicates succesfully.",
        "success",
    )

    return df_prepared


def return_df_AutoClean_missing_num(df, selected_mode):
    df_prepared = return_df_AutoClean(
        AutoClean(df, mode="manual", missing_num=selected_mode)
    )

    flash(
        f"Imputed missing numbers.",
        "success",
    )

    return df_prepared


def return_df_AutoClean_missing_categ(df, selected_mode):
    df_prepared = return_df_AutoClean(
        AutoClean(df, mode="manual", missing_categ=selected_mode)
    )

    flash(
        f"Imputed missing categories (and text).",
        "success",
    )

    return df_prepared


def return_df_AutoClean_encode_categ(df, selected_mode):
    df_prepared = return_df_AutoClean(
        AutoClean(df, mode="manual", encode_categ=selected_mode)
    )

    flash(
        f"Encoded categories (and text).",
        "success",
    )

    return df_prepared


def return_df_AutoClean_extract_datetime(df, selected_mode):
    df_prepared = return_df_AutoClean(
        AutoClean(df, mode="manual", extract_datetime=selected_mode)
    )

    flash(
        f"Extracted dates.",
        "success",
    )

    return df_prepared


def return_df_AutoClean_outliers(df, selected_mode):
    # this is needed so that the AutoClean outliers detection can handle values moved to .5
    for column_name in df.select_dtypes(include=["Int64"]):
        df[column_name] = df[column_name].astype("Float64")

    try:
        df_prepared = return_df_AutoClean(
            AutoClean(df, mode="manual", outliers=selected_mode)
        )

        flash(
            f"Dealt with outliers.",
            "success",
        )

        return df_prepared
    except Exception as e:
        print(f"Error message: {e}")
        flash(
            f"It seems like the removing of outliers did not work.",
            "warning",
        )
        # flash(f"Error message: {e}", "warning")
        return df

    # print(df_prepared)


def generate_h2o_model(column_name_to_predict):
    # Start the H2O cluster (locally)
    h2o.init()

    # Import a sample binary outcome train/test set into H2O
    train = h2o.import_file(
        "https://s3.amazonaws.com/erin-data/higgs/higgs_train_10k.csv"
    )
    test = h2o.import_file("https://s3.amazonaws.com/erin-data/higgs/higgs_test_5k.csv")

    # Identify predictors and response
    x = train.columns
    y = "response"
    x.remove(y)

    # For binary classification, response should be a factor
    train[y] = train[y].asfactor()
    test[y] = test[y].asfactor()

    # Run AutoML for 20 base models
    aml = H2OAutoML(max_models=5, seed=1)
    aml.train(x=x, y=y, training_frame=train)

    # save the model
    model_path = h2o.save_model(
        model=aml.leader, path=current_app.config["STORED_ML_MODELS_FOLDER"], force=True
    )

    print(str(model_path))

    # # download the model built above to your local machine
    # my_local_model = h2o.download_model(
    #     aml.leader, path="E:\OneDrive\Dokumente\FH-Technikum\Masterarbeit"
    # )

    # View the AutoML Leaderboard
    lb = aml.leaderboard
    print(lb.head(rows=lb.nrows))  # Print all rows instead of default (10 rows)

    return None


def download_file(file_name, type_of_file):
    # This is done so that if the user wants to export the active file,
    # it will always get updated in the normal upload directory (not effifcient, but works)
    set_active_file(get_active_dataset_name(), omit_flash_message=True)

    folder_name = ""
    if type_of_file == "dataset":
        folder_name = current_app.config["UPLOAD_FOLDER"]
    elif type_of_file == "ml_model":
        folder_name = current_app.config["STORED_ML_MODELS_FOLDER"]
    else:
        flash("No suitable type_of_file option given for downloading files", "warning")
        return None

    full_path = os.path.join(current_app.root_path, folder_name, file_name)
    print(full_path)

    flash("File was sent to your browser", "success")
    return send_file(full_path, as_attachment=True)
