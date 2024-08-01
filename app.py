from flask import Flask, request, render_template, send_file
from scholarly import scholarly
from urllib.parse import urlparse
import re
import csv
import requests
from io import StringIO

app = Flask(__name__)

BASE_IMPACT_FACTOR = 10

def calculate_impact_factor(num_citations):
    return round(num_citations / BASE_IMPACT_FACTOR, 3)

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def find_doi(title):
    url = f"https://api.crossref.org/works?query.bibliographic={title}"
    response = requests.get(url)
    data = response.json()
    try:
        doi = data['message']['items'][0]['DOI']
        return doi
    except (KeyError, IndexError):
        return "DOI not found"

def get_journal_name_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    data = response.json()
    try:
        journal_name = data['message']['container-title'][0]
        return journal_name
    except KeyError:
        return "Journal name not found"

def retrieve_scholar_info(query, max_results=10):
    search_query = scholarly.search_pubs(query)
    results = []

    count = 0
    while count < max_results:
        try:
            publication = next(search_query)

            title = clean_text(publication['bib']['title'])
            authors = [clean_text(author) for author in publication['bib']['author']]
            main_author = authors[0]
            year = publication['bib']['pub_year']

            eprint_url = publication.get('eprint_url', '')
            journal_homepage = ''
            if eprint_url:
                parsed_url = urlparse(eprint_url)
                journal_homepage = f"{parsed_url.scheme}://{parsed_url.netloc}"

            num_citations = publication['num_citations'] if 'num_citations' in publication else 0
            impact_factor = calculate_impact_factor(num_citations)

            citation_url = publication.get('pub_url', '')

            doi = find_doi(title)
            journal_name = "N/A"
            if doi != "DOI not found":
                journal_name = get_journal_name_from_doi(doi)

            results.append({
                "Title": title,
                "Authors": ', '.join(authors),
                "Main Author": main_author,
                "Year": year,
                "Journal Homepage": journal_homepage,
                "Impact Factor": impact_factor,
                "Citation URL": citation_url,
                "Number of Citations": num_citations,
                "DOI": doi,
                "Journal Name": journal_name
            })

            count += 1

        except StopIteration:
            break
        except KeyError as e:
            print(f"Key error: {e} in publication: {publication}")
        except Exception as e:
            print(f"Error processing publication: {e}")

    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = retrieve_scholar_info(query)
        return render_template('results.html', results=results)

    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_csv():
    results = request.form.get('results')
    if not results:
        return "No data to download", 400

    # Prepare CSV
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Title", "Authors", "Main Author", "Year", "Journal Homepage", "Impact Factor", "Citation URL", "Number of Citations", "DOI", "Journal Name"])
    for result in results:
        writer.writerow([
            result['Title'],
            result['Authors'],
            result['Main Author'],
            result['Year'],
            result['Journal Homepage'],
            result['Impact Factor'],
            result['Citation URL'],
            result['Number of Citations'],
            result['DOI'],
            result['Journal Name']
        ])
    si.seek(0)

    return send_file(
        si,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='scholar_results.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
