import streamlit as st
import tempfile
import os
import pandas as pd
from random import randint
from ParchmentProphet.modules.evaluate import compare_samples_nd, compute_average_vector_scores
import altair as alt
import json
df = pd.DataFrame()

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")

def create_summary_stats(data, label):
    df_expanded = pd.json_normalize(data)
    stats = df_expanded.agg(['mean', 'min', 'max', 'std']).T.reset_index()
    stats.columns = ['Feature', 'Mean', 'Min', 'Max', 'Std Deviation']
    stats['Label'] = label
    return stats

def create_error_bar_plot(human_stats, ai_stats, feature):
    # Filter data for the specific feature
    human_data = human_stats[human_stats['Feature'] == feature]
    ai_data = ai_stats[ai_stats['Feature'] == feature]

    # Create DataFrame for plotting
    plot_data = pd.DataFrame({
        'Source': ['Human', 'AI'],
        'Mean': [human_data['Mean'].values[0], ai_data['Mean'].values[0]],
        'Min': [human_data['Min'].values[0], ai_data['Min'].values[0]],
        'Max': [human_data['Max'].values[0], ai_data['Max'].values[0]]
    })

    # Determine the y-axis domain
    y_min = plot_data['Min'].min() * 0.9  # Adding some padding
    y_max = plot_data['Max'].max() * 1.1  # Adding some padding

    # Create base chart
    base = alt.Chart(plot_data).encode(
        x=alt.X('Source:O', title='Source')
    )

    # Create rule for min to max range with increased stroke width
    errorbars = base.mark_rule(strokeWidth=6, color="white").encode(
        y=alt.Y('Min:Q', scale=alt.Scale(domain=(y_min, y_max))),
        y2='Max:Q'
    )

    # Create points for the mean values
    points = base.mark_point(filled=True, size=250, opacity=1).encode(
        y='Mean:Q'
    )


    # Combine the error bars and points
    chart = errorbars + points

    # Return the chart
    return chart.properties(
        title=f''
    )


def process_data(data):
    results = []
    model_number = 0.1

    for entry in data:
        file = entry['files'][0]
        with open(file, 'r') as f:
            content = f.read()
            model_sections = content.split('*****')
            
            for model_section in model_sections:
                model_section = model_section.strip()
                if model_section:
                    parts = model_section.split('[----]')
                    batch_entries = []
                    for i in range(0, len(parts) - 1, 2):
                        human_text = parts[i].strip()
                        ai_text = parts[i + 1].strip()

                        batch_entries.append({
                            'human_generated': human_text,
                            'ai_generated': ai_text
                        })

                    # Compute linguistic similarity for the current batch
                    lin_individual_scores, lin_avg_distance, lin_min_distance, lin_max_distance, lin_std_dev_distance = compare_samples_nd(batch_entries)

                    # Compute average vector scores for the current batch
                    con_avg_distance, con_min_distance, con_max_distance, con_std_dev_distance, con_avg_angle, con_min_angle, con_max_angle, con_std_dev_angle = compute_average_vector_scores(batch_entries)

                    # Store the results for the current model version
                    results.append({
                        'ai_sample': ai_text,
                        'human_sample': human_text,
                        'model_version': f'{model_number:.1f}',
                        'linguistic_scores': lin_individual_scores,
                        'lin_avg_distance': lin_avg_distance,
                        'lin_min_distance': lin_min_distance,
                        'lin_max_distance': lin_max_distance,
                        'lin_std_dev_distance': lin_std_dev_distance,
                        'con_avg_distance': con_avg_distance,
                        'con_min_distance': con_min_distance,
                        'con_max_distance': con_max_distance,
                        'con_std_dev_distance': con_std_dev_distance,
                        'con_avg_angle': con_avg_angle,
                        'con_min_angle': con_min_angle,
                        'con_max_angle': con_max_angle,
                        'con_std_dev_angle': con_std_dev_angle,
                    })

                    model_number += 0.1

    # Create a DataFrame from the results
    df = pd.DataFrame(results)
    
    return df

# Main layout

# Create a column layout for centering
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("AI Model Evaluation")

    st.markdown("""
    ### Overview
    This application compares human-generated against AI-generated text to evaluate their linguistic and conceptual similarities. By conducting this evaluation across multiple models, you can gain insights into the performance of AI models in generating human-like text. 

    ### How to Use
    1. **Upload Files:** Use the form below to upload a text file containing your evaluation data.
                
    2. **Submit:** Click the 'Submit' button to process and evaluate the content.
                
    3. **View Results:** Examine the visualizations and metrics to understand how the AI models compare to your human generated baselines.
    """)

    with st.expander("File Format Requirements"):
        st.markdown("""
        Your uploaded evaluation data must be in the following format.

        - The file should be in plain text format with a .txt extension.
        - Each file should contain multiple sections separated by `*****`, these sections designate your model.
        - Within each model, human and AI-generated text pairs should be separated by `[----]`. They must be provided in pairs.
        - Example:

            ```
            Human text 1
            [----]
            AI text 1
            [----]
            Human text 2
            [----]
            AI text 2
            *****
            Human text 3
            [----]
            AI text 3
            ...
            ```
                    
        The more samples you have within each model, and the more models you have, the more value you will get from the evaluation. You can test the platform with the sample data provided below.
        """)

    st.markdown("""
    ### Sample Data
    To test the tool yourself, you can download the sample .txt data below. This data contains human-generated and AI-generated text samples ready for evaluation.
    """)



    # Button to download sample data
    with open("eval_data.txt", "r") as file:
        btn = st.download_button(
            label="Download Sample Data",
            data=file,
            file_name="eval_data.txt",
            mime="text/plain"
        )

    st.divider()

    # Form for inputs
    with st.form(key='input_form'):
        files = st.file_uploader('Upload Evaluation Data', type=['txt'], accept_multiple_files=True)
        submit = st.form_submit_button(label='Submit')

        if submit:

            data = []

            if files:
                # Create temp files for human generated content
                temp_files = []
                for file in files:
                    temp_file = tempfile.NamedTemporaryFile(delete=False)
                    temp_file.write(file.read())
                    temp_file.close()
                    temp_files.append(temp_file.name)

                # Store the form data
                data.append({
                    'files': temp_files,
                })

                df = process_data(data)
if not df.empty:

    st.divider()

    feature_descriptions = {
        "type_token_ratio": "This measures the variety of vocabulary used in the text. A higher ratio indicates a more diverse word choice.",
        "hapax_legomena_ratio": "This shows the proportion of words that appear only once in the text. A higher ratio suggests more unique and less repetitive vocabulary.",
        "average_common_bigram_frequency": "This looks at the average frequency of common two-word sequences (bigrams) in the text. A higher value indicates more repetitive use of certain phrases or expressions.",
        "flesch_kincaid_reading_ease_score": "This score estimates how easy or difficult the text is to read. Higher scores mean the text is easier to understand.",
        "gunning_fog_index_score": "This score estimates the number of years of formal education a person might need to easily understand the text on the first reading. A higher score suggests the text is more complex and harder to comprehend.",
        "use_of_passive_voice": "This measures how often passive voice is used in the text. A value of 0 indicates that passive voice was not detected in the sample."
    }

    #### Visualizations ####
    # Ensure unique and sorted model_version values for the scale
    unique_model_versions = sorted(df['model_version'].unique())

    ### Linguistic Similarity ###
    # Line graph of model_version vs lin_avg_distance
    base_linguistic = alt.Chart(df).mark_line(point=True, color='lightblue').encode(
        x=alt.X('model_version:N', axis=alt.Axis(title='Model Version', grid=True), scale=alt.Scale(domain=unique_model_versions)),
        y=alt.Y('lin_avg_distance:Q', axis=alt.Axis(title='Average Linguistic Distance', grid=True)),
        tooltip=['model_version', 'lin_avg_distance']
    ).properties(
        width=600,
        height=400
    ).interactive()

    ### Conceptual Similarity ###
    # Prepare data for the combined line graph
    df_melted = df.melt(id_vars=['model_version'], value_vars=['con_avg_distance', 'con_avg_angle'], 
                        var_name='metric', value_name='value')

    # Combined line graph of model_version vs con_avg_distance and con_avg_angle
    base_combined = alt.Chart(df_melted).mark_line(point=True).encode(
        x=alt.X('model_version:N', axis=alt.Axis(title='Model Version', grid=True), scale=alt.Scale(domain=unique_model_versions)),
        y=alt.Y('value:Q', axis=alt.Axis(title='Value', grid=True)),
        color=alt.Color('metric:N', title='Metric', scale=alt.Scale(domain=['con_avg_distance', 'con_avg_angle'], range=['#87CEFA', '#FFB6C1'])),
        tooltip=['model_version', 'metric', 'value']
    ).properties(
        width=600,
        height=400
    ).interactive()

    st.markdown("# Model Effectiveness by Version")

    # Layout with columns for responsiveness
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Linguistic Similarity")
        with st.expander("Chart Description"):
            st.write("This chart shows the average Euclidian distance between lingustic features for each model version. Lower values represent models that can produce text closely matching the human generated linguistic style. Lower values are better, with a value of 0 representing generated text that is identical to its human sample.")
        st.altair_chart(base_linguistic, use_container_width=True)

    with col2:
        st.subheader("Conceptual Similarity")
        with st.expander("Chart Description"):
                st.write("This chart shows the average Euclidian distance and angle between textual vectors representing your samples. In theory, lower values represent models that can produce text that is conceptually similar and topically cohesive compared with your human samples.")        
        st.altair_chart(base_combined, use_container_width=True)

    st.markdown("----")
    st.markdown("# Best vs Worst Model Comparison")
    
    col3, col4 = st.columns(2)

    with col3:
        st.subheader(f"Best Model: v{df['model_version'].iloc[df['lin_avg_distance'].idxmin()]}")

        best_model = df.loc[df['lin_avg_distance'].idxmin()]

        best_model_report = {
            "Average Linguistic Distance": best_model['lin_avg_distance'],
            "Minimum Linguistic Distance": best_model['lin_min_distance'],
            "Maximum Linguistic Distance": best_model['lin_max_distance'],
            "Standard Deviation Linguistic Distance": best_model['lin_std_dev_distance'],
            "Average Conceptual Distance": best_model['con_avg_distance'],
            "Minimum Conceptual Distance": best_model['con_min_distance'],
            "Maximum Conceptual Distance": best_model['con_max_distance'],
            "Standard Deviation Conceptual Distance": best_model['con_std_dev_distance'],
            "Average Conceptual Angle": best_model['con_avg_angle'],
            "Minimum Conceptual Angle": best_model['con_min_angle'],
            "Maximum Conceptual Angle": best_model['con_max_angle'],
            "Standard Deviation Conceptual Angle": best_model['con_std_dev_angle']            
        }

        # Convert the dictionary to a DataFrame
        best_model_report = pd.DataFrame(best_model_report.items(), columns=['Metric', 'Value'])

        m1, m2, m3 = st.columns(3)
        # get to 2sf
        m1.metric(label="Average Linguistic Distance", value=f"{round(best_model['lin_avg_distance'],2 )}")
        m2.metric(label="Average Conceptual Distance", value=f"{round(best_model['con_avg_distance'], 2)}")
        m3.metric(label="Average Conceptual Angle", value=f"{round(best_model['con_avg_angle'], 2)}")

        st.markdown("### Linguistic Scores")
        st.markdown("The section below contains error bar graphs for each measured linguistic feature.")
        human_summary_stats = create_summary_stats(best_model['linguistic_scores']['Human Features'], 'Human')
        ai_summary_stats = create_summary_stats(best_model['linguistic_scores']['AI Features'], 'AI')

        # Get the list of features
        features = human_summary_stats['Feature'].unique()

        # Loop through each feature and create a chart
        for feature in features:
            # Take feature, convert _ to spaces and apply title case
            title_feature = feature.replace('_', ' ').title()
            with st.expander(f"{title_feature}"):
                if feature in feature_descriptions:
                    st.write(f"**Description:** {feature_descriptions[feature]}")
                chart = create_error_bar_plot(human_summary_stats, ai_summary_stats, feature)
                st.altair_chart(chart, use_container_width=True)



        st.markdown("### Example Generation")
        with st.expander("Human Sample"):
            st.write(best_model['human_sample'])
        with st.expander("AI Sample"):
            st.write(best_model['ai_sample'])

    with col4:
        st.subheader(f"Worst Model: v{df['model_version'].iloc[df['lin_avg_distance'].idxmax()]}")

        worst_model = df.loc[df['lin_avg_distance'].idxmax()]

        worst_model_report = {
            "Average Linguistic Distance": worst_model['lin_avg_distance'],
            "Minimum Linguistic Distance": worst_model['lin_min_distance'],
            "Maximum Linguistic Distance": worst_model['lin_max_distance'],
            "Standard Deviation Linguistic Distance": worst_model['lin_std_dev_distance'],
            "Average Conceptual Distance": worst_model['con_avg_distance'],
            "Minimum Conceptual Distance": worst_model['con_min_distance'],
            "Maximum Conceptual Distance": worst_model['con_max_distance'],
            "Standard Deviation Conceptual Distance": worst_model['con_std_dev_distance'],
            "Average Conceptual Angle": worst_model['con_avg_angle'],
            "Minimum Conceptual Angle": worst_model['con_min_angle'],
            "Maximum Conceptual Angle": worst_model['con_max_angle'],
            "Standard Deviation Conceptual Angle": worst_model['con_std_dev_angle']            
        }

        # Convert the dictionary to a DataFrame
        worst_model_report = pd.DataFrame(worst_model_report.items(), columns=['Metric', 'Value'])

        m1, m2, m3 = st.columns(3)
        # get to 2sf
        m1.metric(label="Average Linguistic Distance", value=f"{round(worst_model['lin_avg_distance'],2 )}")
        m2.metric(label="Average Conceptual Distance", value=f"{round(worst_model['con_avg_distance'], 2)}")
        m3.metric(label="Average Conceptual Angle", value=f"{round(worst_model['con_avg_angle'], 2)}")

        st.markdown("### Linguistic Scores")
        st.markdown("The section below contains error bar graphs for each measured linguistic feature.")
        human_summary_stats = create_summary_stats(worst_model['linguistic_scores']['Human Features'], 'Human')
        ai_summary_stats = create_summary_stats(worst_model['linguistic_scores']['AI Features'], 'AI')

        # Get the list of features
        features = human_summary_stats['Feature'].unique()

        # Loop through each feature and create a chart
        for feature in features:
            # Take feature, convert _ to spaces and apply title case
            title_feature = feature.replace('_', ' ').title()
            with st.expander(f"{title_feature}"):
                if feature in feature_descriptions:
                    st.write(f"**Description:** {feature_descriptions[feature]}")
                chart = create_error_bar_plot(human_summary_stats, ai_summary_stats, feature)
                st.altair_chart(chart, use_container_width=True)



        st.markdown("### Example Generation")
        with st.expander("Human Sample"):
            st.write(worst_model['human_sample'])
        with st.expander("AI Sample"):
            st.write(worst_model['ai_sample'])

    # Clean up temporary files
    for entry in data:
        for file in entry['files']:
            os.remove(file)


