# 🤖 Mitt Speciella Barn – AI Assistant

An AI-powered assistant that helps users find relevant information and resources from the Swedish website **[mittspeciellabarn.se](https://mittspeciellabarn.se/)**, dedicated to supporting families with children who have disabilities.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API%20v4-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Agents-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🔍 Features

- 💬 **Natural Language Queries**: Ask questions in Swedish, Arabic, English, and more.
- 🧠 **Semantic Search**: Uses OpenAI embeddings and cosine similarity to retrieve the most relevant content.
- 🌐 **Web Scraper Plugin**: Custom plugin scrapes and indexes website pages.
- 🔧 **Function Calling with OpenAI**: Dynamically routes user queries to search functions via streaming.
- 📊 **Interactive Output**: Displays structured HTML responses including function calls and results.

## 🛠️ Tech Stack

- OpenAI API (`gpt-4`, `text-embedding-3-small`)
- LangChain Agents (`ChatCompletionAgent`)
- Async Python (`asyncio`)
- Pandas, NumPy
- HTML rendering for interactive output
- Custom plugin architecture for modular extension

## 📦 Installation & Setup

### Prerequisites

1. Python 3.8 or higher
2. An OpenAI API key (You can get it from [OpenAI's platform](https://platform.openai.com/))

### Steps to Run the Project

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/mitt-speciella-barn-assistant.git
    cd mitt-speciella-barn-assistant
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Your OpenAI API Key**
    - Set the `OPENAI_API_KEY` environment variable:
    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    ```

4. **Run the Jupyter Notebook**
    - Start a Jupyter notebook server:
    ```bash
    jupyter notebook
    ```
    - Open the notebook and run the cells sequentially.

> Built with ❤️ to empower families navigating support systems.

## 🚀 Use Case

Perfect for non-technical users (e.g. parents or social workers) looking for:
- How to apply for financial aid.
- Services and community support for children with special needs.
- Specific activities or events from the website.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
