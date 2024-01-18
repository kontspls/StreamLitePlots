import pandas as pd
import streamlit as st
import plotly.express as px


# Expander to allow for better visualization
intro_info = st.expander("Introduction", expanded=True)

# Introduction
with intro_info:
    st.title("StreamLitePlots")
    st.write(
        """
        Welcome to StreamLitePlots, a lightweight visualization app made with leftover code from a past project. 
        Its purpose is to efficiently display a selection of common plots. 
        
        While originally created for the datasets of a specific company, it is capable of 
        producing plots for most datasets in .csv format. All visualizations provide interactive functionality.
        
        Please note that this app is not optimized for handling large datasets. 
        Users are advised to have some familiarity with their dataset before loading it into the app, 
        as certain visualizations can be computationally intensive when dealing with sizable datasets or variables
        with certain format types. 
        
        To begin, upload your file below and select your choices as they appear. You can also rerun the app 
        or change themes through the options button in the top right corner. 
        For easier navigation between graphs, consider folding this introduction container, the file uploader,
        and the file viewer after uploading your file.    
        """
    )

# Create file uploader
file_uploader = st.expander("File Uploader", expanded=True)
with file_uploader:
    base_sheet = st.file_uploader(label="Upload File", type="csv", key="uploaded_file")

if base_sheet is not None:
    df = pd.read_csv(base_sheet, index_col=0)
    df.reset_index(inplace=True)

    # Write to session.state if not present already, otherwise overwrite previous entry
    if 'data' not in st.session_state:
        st.session_state['data'] = df
    elif 'data' in st.session_state:
        st.session_state['data'] = df

# Warn and prevent continuation of the script when no file is uploaded
elif base_sheet is None:
    st.warning("Please enter a files before we can continue.")
    st.cache_data.clear()
    st.stop()

# Create Checkbox to show uploaded file
show_file = st.checkbox('Show Uploaded File', key="show_file")
if show_file:
    st.subheader("Uploaded File")
    st.dataframe(data=st.session_state.data)

# Create sidebar Selectbox to select type of visualisation
with (st.sidebar):
    type_of_plot = st.selectbox(
        "What kind of visualization would you like to see?", (
            "Scatter Plot",
            "Timeline",
            "Histogram",
            "Categorical Variables Charts"
        ),
        index=None,
        placeholder="Select Graph Type...",
    )

if type_of_plot == "Scatter Plot":
    with (st.sidebar):
        # Information about function
        st.write(
            """
        Please select the variables to be used on the graphs. Check the checkbox below if
        you wish to view a 3D scatter plot of three variables instead of two.
        """
        )
        # Selectboxes for variables
        scatter_var_x = st.selectbox("Select x variable:", df.columns, index=0)
        scatter_var_y = st.selectbox("Select y variable:", df.columns, index=1)

        st.divider()
        # Checbox to allow a third variable
        three_d = st.checkbox("Visualize 3 variables")

        if three_d:
            # Selectbox for third variable
            scatter_var_z = st.selectbox("Select z variable:", df.columns, index=1)

    # 3D Scatterplot function with 3 variables if third variable checkbox is checked
    if three_d:
        def draw_3d_scatter_plot(uploaded_file, x, y, z):
            fig = px.scatter_3d(
                uploaded_file,
                x=x,
                y=y,
                z=z,
                template='seaborn',
                color_discrete_sequence=["darkturquoise"]
            )
            st.plotly_chart(fig)

        # Scatter plot with 3 variables
        draw_3d_scatter_plot(df, scatter_var_x, scatter_var_y, scatter_var_z)

    # Scatterplot function with 2 variables if third variable checkbox is not checked
    else:
        def draw_scatter_plot(uploaded_file, x, y):
            fig = px.scatter(uploaded_file, x=x, y=y, title='Scatter Plot')
            st.plotly_chart(fig)

        draw_scatter_plot(df, scatter_var_x, scatter_var_y)

if type_of_plot == "Timeline":
    with (st.sidebar):
        # Information about function
        st.write(
            """
        Please select the variables to be used on the graphs. For clear results, 
        variable x should be a date with no duplicate entries and the variable or variables
        selected for y axis should be either continuous or discrete. 
        """
                 )

        # Select 'Date' variable for x-axis
        line_var_x = st.selectbox("Select 'Date' variable for x axis", df.columns, index=0)

        # Ensure the format is correct, otherwise catch error/exception with warning
        try:
            df[line_var_x] = pd.to_datetime(df[line_var_x], format="ISO8601")
        except (ValueError, Exception):
            st.warning(
                """
            The column you have selected does not have a valid date format.
            Please make sure the format of the column's values is ISO8601.
            """
                       )
            st.stop()

        col1, col2 = st.columns(2)

        # Select starting date
        with col1:
            line_start_date = st.date_input(
                "Starting date:",
                value=df[line_var_x].min(),
                min_value=df[line_var_x].min(),
                max_value=df[line_var_x].max(),
                format="YYYY-MM-DD"
            )

        # Select end date
        with col2:
            line_end_date = st.date_input(
                "End date:",
                value=df[line_var_x].max(),
                min_value=line_start_date,
                max_value=df[line_var_x].max(),
                format="YYYY-MM-DD"
            )

        # Create dataframe based on date selection
        try:
            line_needed_data = df.loc[
                (df[line_var_x] >= str(line_start_date)) & (df[line_var_x] <= str(line_end_date))].copy()
        # Catch error in case user puts wrong manual dates in date selection
        except TypeError:
            st.warning("Please select dates that are valid.")
            st.stop()

        st.divider()
        # Select variables for y axis
        options = line_needed_data.columns.tolist()

        # Add option to add variables, use container method
        # to place the checkbox below the multiselect function
        container = st.container()
        all_choices = st.checkbox("Select all variables")
        with container:
            if all_choices:
                selected_options = st.multiselect(
                    'Select variable(s) for y axis:',
                    options, options,
                    disabled=True
                )
            else:
                selected_options = st.multiselect(
                    'Select variable(s) for y axis:',
                    options, default=options[1]
                )

    # Line plot function
    def draw_line_plot(uploaded_file, x, y):
        fig = px.line(uploaded_file, x=x, y=y, title='Line Chart')
        st.plotly_chart(fig)


    try:
        draw_line_plot(line_needed_data, line_var_x, selected_options)

    # Catch error in case one variable is a different format than the others
    except ValueError:
        st.warning(
            """
            One of  the variables has a different format type. 
            Please remove the variable to continue.
            """
        )
        st.stop()

if type_of_plot == "Histogram":
    with (st.sidebar):

        # Information about function
        st.write(
            """
        Please select whether you would like to see a univariate or multivariate histogram. 
        Keep in mind that in the case of a multivariate histogram, 
        all the variables need to have the same format type.
        """
        )
        # Selectbox to allow user to choose number of variables
        type_of_histogram = st.selectbox(
            "Select number of variables for Histogram",
            ["Univariate", "Multivariate"]
        )

    if type_of_histogram == "Univariate":

        # Single variable selection for univariate histogram
        with (st.sidebar):
            feature_x = st.selectbox("Select Variable", df.columns, index=0)

            # Function for plot
            def draw_univ_distribution_plot(uploaded_file, x):
                fig = px.histogram(
                    uploaded_file,
                    x=x, title='Univariate Histogram',
                    marginal='box'
                )
                fig.update_layout(bargap=0.05)
                st.plotly_chart(fig)

        draw_univ_distribution_plot(df, feature_x)

    elif type_of_histogram == "Multivariate":

        with (st.sidebar):

            # Parameter options for histogram function when multiple variables need to be visualized
            histogram_types = ['relative', 'group', 'overlay', 'stack']

            # Selection of variables
            selected_type_of_histogram = st.selectbox(
                'Select type of histogram:', histogram_types, help=(
                    """
                    For more information on types of histograms, 
                    please consult the plotly documentation at 
                    https://plotly.github.io/plotly.py-docs/generated/plotly.express.histogram.html
                    """
                )
            )

            # Variable options derived from dataset columns
            options_hist = df.columns.tolist()

            selected_options = st.multiselect(
                'Select variables:',
                options_hist, options_hist[0],
            )

        # Function for histogram
        def draw_distribution_plot_multi(uploaded_file, x):
            fig = px.histogram(uploaded_file, x=x, title='Multivariate Histogram',
                               barmode=selected_type_of_histogram)
            fig.update_layout(bargap=0.05)
            st.plotly_chart(fig)

        # Catch error in case variables have different format types
        try:
            draw_distribution_plot_multi(df, selected_options)

        except ValueError:
            st.warning(
                """
                One of  the variables has a different format type. 
                Please remove the variable to continue.
                """
            )
            st.stop()

if type_of_plot == "Categorical Variables Charts":
    with (st.sidebar):
        # Information about function
        st.write(
            """
        Please select the x variable. Keep in mind the following: 
        1) The app will automatically attempt to convert the values of the column you 
        selected into a Pandas "Category" data type. For proper visualisation, 
        the variable selected must be categorical.
        2) The "Pie Chart" can be computationally intensive depending on the variables selected 
        and the number of values.
        """
        )
        # Select variable for x-axis and catch error is wrong form/type of variable is selected
        bar_var_x = st.selectbox("Select categorical variable for x axis", df.columns, index=0)

        try:
            df[bar_var_x] = df[bar_var_x].astype("category")

        except (ValueError, Exception):
            st.warning("The variable you have selected cannot be viewed as a category.")
            st.stop()

        bar_var_y = st.selectbox("Select values for the categorical variable in x axis", df.columns, index=1)

        # Parameter options for barplot
        bar_mode_options = ['relative', 'group', 'overlay', 'stack']

        selected_type_of_barmode = st.selectbox(
            'Select type of barplot:', bar_mode_options, help=(
                """
            For more information on types of bar plots, 
            please please consult the plotly documentation at 
            https://plotly.com/python-api-reference/generated/plotly.express.bar
            """
            )
        )

        # Option to view data for selected dates if a date column exists in the dataset
        choose_date = st.checkbox("View charts for selected dates only")

        if choose_date:
            bar_time_period = st.selectbox("Select date variable for charts", df.columns, index=0)
            # Ensure the format is correct, otherwise catch error/exception with warning
            try:
                df[bar_time_period] = pd.to_datetime(df[bar_time_period], format="ISO8601")
            except (ValueError, Exception):
                st.warning(
                    """
                    The column you have selected does not have a valid date format. 
                    Please make sure the format of the column's values is ISO8601.
                    """
                           )
                st.stop()

            # Select start and end dates
            col1, col2 = st.columns(2)

            with col1:
                bar_start_date = st.date_input(
                    "Starting date:",
                    value=df[bar_time_period].min(),
                    min_value=df[bar_time_period].min(),
                    max_value=df[bar_time_period].max(),
                    format="YYYY-MM-DD"
                )
            with col2:
                bar_end_date = st.date_input(
                    "End date:",
                    value=df[bar_time_period].max(),
                    min_value=bar_start_date,
                    max_value=df[bar_time_period].max(),
                    format="YYYY-MM-DD"
                )
            # Create dataframe with selected dates
            try:
                bar_needed_data = df.loc[
                    (df[bar_time_period] >= str(bar_start_date)) & (
                            df[bar_time_period] <= str(bar_end_date))].copy()
            # Catch error in case user puts wrong manual dates in date selection and checks period
            except TypeError:
                st.warning("Please select dates that are valid.")
                st.stop()

    # Create tabs for two different charts
    cattab1, cattab2 = st.tabs(["Bar Chart", "Pie Chart"])

    # Create functions for bar and pie charts
    def show_bar_chart(uploaded_file, x, y):
        fig = px.bar(uploaded_file, x=x, y=y, title='Bar Chart', barmode=selected_type_of_barmode)
        st.plotly_chart(fig)

    def draw_pie_chart(uploaded_file, x, y):
        fig = px.pie(uploaded_file, values=y, names=x, title='Pie Chart')
        st.plotly_chart(fig)

    # The user has selected specific dates for the graphs
    if choose_date:
        with cattab1:
            # Plot bar chart and catch error
            try:
                show_bar_chart(bar_needed_data, bar_var_x, bar_var_y)
            except ValueError:
                st.warning(
                    """
                    One of  the variables has a different format type. 
                    Please remove the variable to continue.
                    """
                )
                st.stop()

        with cattab2:
            # Plot pie chart and catch error
            try:
                draw_pie_chart(bar_needed_data, bar_var_x, bar_var_y)
            except ValueError:
                st.warning(
                    """
                    One of  the variables has a different format type. 
                    Please remove the variable to continue.
                    """
                )
                st.stop()

    # The user has not selected dates
    else:
        with cattab1:
            # Plot bar chart and catch error
            try:
                show_bar_chart(df, bar_var_x, bar_var_y)
            except ValueError:
                st.warning(
                    """
                    One of  the variables has a different format type. 
                    Please remove the variable to continue.
                    """
                )
                st.stop()

        with cattab2:
            # Plot pie chart and catch error
            st.info(
                """
                Remember that the pie chart can be computationally 
                intensive, especially if both the x variable and the variable selected for values are not categorical!
                """
            )
            if st.button("Got it, show me anyway"):
                try:
                    draw_pie_chart(df, bar_var_x, bar_var_y)
                except ValueError:
                    st.warning(
                        """
                        One of  the variables has a different format type. 
                        Please remove the variable to continue.
                        """
                    )
                    st.stop()
