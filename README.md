# ParchmentProphet-ui

ParchmentProphet-ui is a Streamlit-based application designed to evaluate and compare human-generated and AI-generated text samples. This tool leverages the [ParchmentProphet](https://github.com/Sankgreall/ParchmentProphet) package to compute linguistic and conceptual similarity metrics between human and AI text samples.

## Features

- Upload text files containing human and AI-generated text samples for evaluation.

- Compare the performance of different AI models based on the provided text samples.

- View summary statistics and error bar plots for various linguistic features.

- Explore example text generations for the best and worst performing models.

## File Format Requirements

Your uploaded evaluation data must adhere to the following format:

- Plain text format with a .txt extension.
- Each file should contain multiple sections separated by `*****`, representing different models.
- Within each model section, pairs of human and AI-generated text should be separated by `[----]`.
- Example
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

## Installation

1. Clone the repository

```
git clone https://github.com/Sankgreall/ParchmentProphet-ui.git
cd ParchmentProphet-ui
```

2. Copy `.env.sample` to `.env` and fill in the required variables. You will need an OpenAI API key.

3. Build the Docker image

```
docker build -t parchmentprophet-ui .
```

4. Run the Docker container
```
docker run -p 8501:8501 parchmentprophet-ui
```

5. Access the application on `http://localhost:8501
