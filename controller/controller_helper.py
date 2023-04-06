from flask import render_template, current_app, redirect, url_for, flash
import os
import pandas as pd
import yaml


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

    try:
        df = pd_read_function(
            file_path,
            encoding="latin1",
            header=header_value,
            sep=file_separator,
            index_col=index_value,
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
        create_user_file_config(user_file_name, create_config_dict())
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


def create_config_dict(has_header=False, file_separator=",", has_index=False):
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
    }

    user_file_configs["has_header"]["value"] = True if has_header else False

    user_file_configs["file_separator"]["value"] = (
        file_separator if file_separator else ","
    )

    user_file_configs["has_index"]["value"] = True if has_index else False

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
    index_name = active_df.index.name
    new_row = {}
    new_row_list = []
    for column in active_df.columns:
        if column in add_row_dict:
            new_row_list.append(add_row_dict[column])
            new_row[column] = add_row_dict[column]
            print(f"{column}={add_row_dict[column]}")

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

    # print(df_prepared)

    if get_active_user_file_config()["has_index"]["value"] == True:
        df_prepared = df_prepared.set_index(index_name).reset_index()
        # print(df_prepared)
    # else:
    #     new_row_list.insert(0, new_row)
    #     df_prepared = pd.concat(
    #         [pd.DataFrame(new_row_list), active_df], ignore_index=True
    #     )

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
