# Sentiment Analysis of Nigeria's Economic News (2021–Present)
## Project Objective

The primary objective of this project is to **analyze the sentiment of news articles** to uncover the emotional tone and opinions conveyed in media content related to **Nigeria’s economy**. The analysis spans from **2021 to the present**, focusing on how the media has shaped and presented economic narratives over time. This project aims to answer:

- What general sentiment is conveyed in economic news coverage?
- Has the emotional tone shifted over the years?
- How might media sentiment reflect or influence public and investor perception?

---

##  Research Summary & Key Findings

This research is centered on the analysis of **7,760 articles** sourced from the *BusinessDay Nigeria* website, a reputable media outlet known for its coverage of Nigeria’s financial and economic landscape.

### Sentiment Distribution

After preprocessing and sentiment analysis, the articles were classified into the following categories:

| Sentiment | Article Count | Percentage |
|-----------|----------------|------------|
| Positive  | 3,038          | 39.1%      |
| Neutral   | 3,007          | 38.8%      |
| Negative  | 1,715          | 22.1%      |

###  Interpretation

- A **significant proportion (78%)** of the articles were either **positive or neutral** in sentiment, suggesting that the media tone around Nigeria’s economy tends to be **optimistic or balanced** rather than pessimistic.
- **Positive sentiment (39.1%)** was the most dominant, indicating frequent media coverage on growth, investment, reforms, or other favorable economic events.
- **Neutral sentiment (38.8%)** shows that many articles were objective or informative without strong emotional language.
- **Negative sentiment (22.1%)**, while the least, still represents a considerable portion, likely highlighting challenges such as inflation, debt, unemployment, or political instability.

These findings help paint a data-driven picture of how economic issues are communicated in the media and can serve as a proxy for public or investor confidence in Nigeria’s economic direction over the past few years.

---

##  Methodology & Technical Documentation

### 1. Data Collection

- **Source**: [https://businessday.ng/tag/bdlead/?amp]
- **Pages Scraped**: 818
- **Total Articles**: 7,760
- **Scraping Tool**: `Selenium`

#### Features Extracted

- Title  
- Author  
- Publication Date  
- Article Excerpt  

####  Challenges & Solutions

| Challenges | Resolution |
|----------|-------------|
| Cloudflare protection & bot detection | Introduced randomized delays, used rotating user agents, and added scroll simulation to mimic human behavior |
| JavaScript-rendered content | Used Selenium instead of static scrapers like `requests` or `BeautifulSoup` |
| Timeout errors & intermittent failures | Implemented retry logic with exception handling |

---

### 2. Preprocessing & Sentiment Analysis

#### 🔧 Preprocessing

- Removed stopwords, and punctuation
- Converted text to lowercase
- Performed tokenization and lemmatization

#### Sentiment Model

- **Tool Used**: `TextBlob` 
- Articles were analyzed for polarity scores and categorized as:
  - **Positive**
  - **Neutral**
  - **Negative**

---

##  Tools & Libraries

- `Python 3.10`
- `Selenium`
- `Pandas`
- `NLTK`, `TextBlob`
- `Matplotlib`, `Seaborn`

---

## Future Improvements

- **Temporal sentiment analysis**: Observe how sentiment changes year-over-year
- **Named Entity Recognition (NER)**: Track companies, politicians, and keywords influencing sentiment
- **Topic modeling**: Cluster articles into topics using LDA or BERTopic
- **Interactive Dashboard**: Create a Streamlit or Dash app for dynamic data exploration

---



