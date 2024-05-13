from flask import Flask, render_template, request, send_from_directory
import pickle
from Bio import Entrez

app = Flask(__name__)

# Set your Entrez credentials
Entrez.email = "Jeffreystijnen0@gmail.com"
# Entrez.api_key = "YourAPIKey"

def search_pubmed(condition, search_terms, selected_article_types):
    if selected_article_types:
        article_types = " OR ".join([f"{atype}" for atype in selected_article_types])
        query = f"({condition}) AND ({search_terms}) AND ({article_types})"
    else:
        query = f"({condition}) AND ({search_terms})"  # Default to broader search if no types selected

    handle = Entrez.esearch(db="pubmed", term=query, retmax=1000)
    record = Entrez.read(handle)
    handle.close()

    return record["IdList"], int(record["Count"])

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    show_download = False
    if request.method == 'POST':
        condition = request.form['condition']
        search_terms = request.form['search_terms']
        selected_article_types = request.form.getlist('article_types')
        
        pmids, total_count = search_pubmed(condition, search_terms, selected_article_types)
        
        # Save all results to a pickle file
        with open('data/pubmed_search_results.pkl', 'wb') as f:
            pickle.dump(pmids, f)
        
        # Limit display to first 15 PMIDs
        display_pmids = pmids[:15]
        results = {'total_count': total_count, 'pmids': display_pmids}
        show_download = True  # Show download button if there are any results
        
    return render_template('index.html', results=results, show_download=show_download)

@app.route('/download')
def download():
    return send_from_directory(directory='.', path='pubmed_search_results.pkl', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
