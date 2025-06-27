from flask import Flask, render_template, request, session, redirect, url_for, send_file, Response
import csv
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = 'supersecretkey'  # Change this in production
ALLOWED_EXTENSIONS = {'csv'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_csv_headers(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        headers = next(reader, [])
    return headers

def load_deal_names_from_csv(csv_path, field):
    deal_names = set()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            value = row.get(field)
            if value:
                deal_names.add(value.strip().lower())
    return deal_names

def cross_reference_deals(existing_csv, new_csv, existing_field, new_field):
    existing_deal_names = load_deal_names_from_csv(existing_csv, existing_field)
    results = []
    with open(new_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            value = row.get(new_field)
            if not value:
                continue
            status = 'New lead' if value.strip().lower() not in existing_deal_names else 'Duplicate'
            results.append({'deal_name': value, 'status': status})
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None
    all_headers = None
    new_headers = None
    selected_all_field = None
    selected_new_field = None
    if request.method == 'POST':
        selected_all_field = request.form.get('all_field')
        selected_new_field = request.form.get('new_field')
        # Step 1: Upload files and show field selection
        if not (selected_all_field and selected_new_field):
            all_deals_file = request.files.get('all_deals')
            new_leads_file = request.files.get('new_leads')
            if not all_deals_file or not new_leads_file or not all_deals_file.filename or not new_leads_file.filename:
                error = 'Please upload both files.'
            elif not (allowed_file(all_deals_file.filename) and allowed_file(new_leads_file.filename)):
                error = 'Only CSV files are allowed.'
            else:
                # Save files with unique names
                all_deals_filename = str(uuid.uuid4()) + '_' + secure_filename(all_deals_file.filename)
                new_leads_filename = str(uuid.uuid4()) + '_' + secure_filename(new_leads_file.filename)
                all_deals_path = os.path.join(app.config['UPLOAD_FOLDER'], all_deals_filename)
                new_leads_path = os.path.join(app.config['UPLOAD_FOLDER'], new_leads_filename)
                all_deals_file.save(all_deals_path)
                new_leads_file.save(new_leads_path)
                session['all_deals_path'] = all_deals_path
                session['new_leads_path'] = new_leads_path
                all_headers = get_csv_headers(all_deals_path)
                new_headers = get_csv_headers(new_leads_path)
                return render_template('index.html', results=None, error=None, all_headers=all_headers, new_headers=new_headers, selected_all_field=None, selected_new_field=None)
        # Step 2: Fields selected, do comparison
        else:
            all_deals_path = session.get('all_deals_path')
            new_leads_path = session.get('new_leads_path')
            if not all_deals_path or not new_leads_path:
                error = 'Session expired or files missing. Please re-upload.'
            else:
                try:
                    results = cross_reference_deals(all_deals_path, new_leads_path, selected_all_field, selected_new_field)
                    session['results'] = results
                    session['selected_new_field'] = selected_new_field
                    session['new_leads_path'] = new_leads_path  # keep for export
                except Exception as e:
                    error = f'Error processing files: {e}'
                # Clean up files after processing
                if os.path.exists(all_deals_path):
                    os.remove(all_deals_path)
                session.pop('all_deals_path', None)
    return render_template('index.html', results=results, error=error, all_headers=all_headers, new_headers=new_headers, selected_all_field=selected_all_field, selected_new_field=selected_new_field)

@app.route('/export')
def export_results():
    export_type = request.args.get('type')
    keep = request.args.get('keep')
    results = session.get('results')
    new_leads_path = session.get('new_leads_path')
    selected_new_field = session.get('selected_new_field')
    if not results or not new_leads_path or not selected_new_field:
        return 'No data to export. Please re-run your comparison.', 400
    # Export only new or duplicate deal names as a CSV
    if export_type in ['new', 'duplicate']:
        filtered = [r for r in results if r['status'].lower() == ('new lead' if export_type == 'new' else 'duplicate')]
        def generate_new_dup():
            yield 'Deal Name,Status\n'
            for row in filtered:
                yield f"{row['deal_name']},{row['status']}\n"
        return Response(generate_new_dup(), mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename={export_type}_deals.csv"})
    # Export the original new leads CSV, filtered by duplicate status
    elif export_type == 'filtered_csv' and keep in ['new', 'duplicate']:
        keep_status = 'New lead' if keep == 'new' else 'Duplicate'
        keep_names = set(r['deal_name'].strip().lower() for r in results if r['status'] == keep_status)
        with open(new_leads_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            fieldnames = reader.fieldnames if reader.fieldnames else []
            rows = [row for row in reader if row.get(selected_new_field, '').strip().lower() in keep_names]
        def generate_filtered():
            yield ','.join(fieldnames) + '\n'
            for row in rows:
                yield ','.join([row.get(f, '') for f in fieldnames]) + '\n'
        return Response(generate_filtered(), mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename={keep}_leads_filtered.csv"})
    else:
        return 'Invalid export type.', 400

if __name__ == '__main__':
    app.run(debug=False) 