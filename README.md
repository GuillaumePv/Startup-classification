# Start-ups classfication

In this repositoty, we can find code to scrap html page and Github Readme form various start-ups.

This repository is a extension of this previous paper: https://www.hbs.edu/ris/Publication%20Files/22-001rev9-30-21_e5960a01-5b10-4aa4-9413-e711e5a2247d.pdf

code based on https://github.com/jorgeguzmanecon/measuring-founding-strategy

## Code structure

```
├── code
│   ├── python      <- Code written in python
│   │    ├── scrapper
│   │    │ 
│   │    ├── text_analysis
│   │    │ 
│   │    ├── NLP Classifier
│   │    │      ├──  Website Classifier
│   │    │      │ 
│   │    │      ├──  GitHub Classifier
│   │    │ 
│   │    ├── utils
│   │    │ 
│   │    ├── driver
│   │    │ 
│   │    ├── old                <- Previous scripts which have been updated in the project
│   │
│   └── Stata            <- Code written in Stata
│
├── data             <- Folder that contains datasets
│
│
├── Readme.md          <- Readme file for information about the project
│
│
├── requirements.txt   <- List of all Python modules required to launch the program
│                         
```
## Librairies

- Gensim :https://towardsdatascience.com/calculating-document-similarities-using-bert-and-other-models-b2c1a29c9630
- Sklearn
- Nltk


## Authors

- Christian Peukert (christian.peukert@unil.ch)
- Anthi Kiouka (anthi.kiouka@unil.ch)
- Guillaume Pavé (guillaumepave@gmail.com)
- Louis Del Perugia ()