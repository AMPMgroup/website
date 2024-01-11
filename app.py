from flask import Flask, render_template, request, url_for
import mysql.connector
import os

app = Flask(__name__)

@app.route('/search', methods=['POST'])
#For database ouput --- files used search_form.html & results.html
def cdr_search():
    pdbid_input = request.form['pdbid']
    pdb_ids = [pdb.strip() for pdb in pdbid_input.split(',')]

    #pdb_id_placeholders = ', '.join(['%s'] * len(pdb_ids))
    antigen_selected = 'Antigen' in request.form
    antibody_selected = 'Antibody' in request.form

    # Connect to the database
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="divya",
        database="my_db"
    )
    mycursor = mydb.cursor()
    
    query_for_cdr = """
    SELECT c.PDBid, c.Chain AS 'Chain',
    c.Loop AS 'Loop', c.Sequence AS Sequence, c.Start_Position AS Start_Position, c.End_Position AS End_Position
    FROM cdr AS c
    WHERE c.PDBid = %s;
    """
    query_for_biophysical = """
    SELECT DISTINCT r.PDBid, r.Residue_id AS Residue_ID, r.Residue_Name AS Name, 
    r.Chain AS 'Chain', r.Residue_Weight AS Weight, r.ResidueVanDerWaals AS ResidueVanDerWaals, 
    r.Residue_Charge AS Charge, r.Residue_Polarity AS Residue_Polarity, 
    r.Solvent_Accessible_SurfaceArea AS SASA, r.Charge AS Charge, r.PHI AS PHI, r.PSI AS PSI, 
    r.Omega AS Omega, r.Chi AS Chi,
    r.Is_Antigen_Chain AS Is_Antigen_Chain
    FROM residue AS r
    WHERE r.PDBid = %s;
    """
    query_for_biophysical_antigen = """
        -- First query for the "Biophysical_properties" table for Antigen
        SELECT DISTINCT r.PDBid, r.Residue_id AS Residue_ID, r.Residue_Name AS Name,
        r.Chain AS 'Chain', r.Residue_Weight AS Weight, r.ResidueVanDerWaals AS ResidueVanDerWaals,
        r.Residue_Charge AS Charge, r.Residue_Polarity AS Residue_Polarity,
        r.Solvent_Accessible_SurfaceArea AS SASA, r.Charge AS Charge, r.PHI AS PHI, r.PSI AS PSI,
        r.Omega AS Omega, r.Chi AS Chi,
        a.Is_Antigen_Chain AS Is_Antigen_Chain
        FROM antigen AS a
        INNER JOIN residue AS r ON a.PDBid = r.PDBid AND r.Is_Antigen_Chain = 'Antigen'
        WHERE r.PDBid = %s AND a.Is_Antigen_Chain = 'Antigen';
    """
    query_for_biophysical_antibody =  """
        -- First query for the "Biophysical_properties" table for Antibody
        SELECT DISTINCT r.PDBid, r.Residue_id AS Residue_ID, r.Residue_Name AS Name,
        r.Chain AS 'Chain', r.Residue_Weight AS Weight, r.ResidueVanDerWaals AS ResidueVanDerWaals,
        r.Residue_Charge AS Charge, r.Residue_Polarity AS Residue_Polarity,
        r.Solvent_Accessible_SurfaceArea AS SASA, r.Charge AS Charge, r.PHI AS PHI, r.PSI AS PSI,
        r.Omega AS Omega, r.Chi AS Chi,
        a.Is_Antigen_Chain AS Is_Antigen_Chain
        FROM antigen AS a
        INNER JOIN residue AS r ON a.PDBid = r.PDBid AND r.Is_Antigen_Chain = 'Antibody'
        WHERE r.PDBid = %s AND a.Is_Antigen_Chain = 'Antibody';
    """

    cdr_data = {}
    biophysical_data = {}
    biophysical_properties_column_names = []

    # Fetch CDR data and store it in cdr_data
    if antibody_selected:
        for pdb_id in pdb_ids:
            mycursor.execute(query_for_cdr, (pdb_id,))
            cdr_results = mycursor.fetchall()
            cdr_column_names = [i[0] for i in mycursor.description]
            for _ in cdr_results:
                pass
            cdr_data[pdb_id] = {
                "column_names": cdr_column_names,
                "results": cdr_results
            }

# Fetch and organize biophysical data
    for pdb_id in pdb_ids:
        query = []
        if antibody_selected and antigen_selected:
            # If both checkboxes are selected, combine antigen and antibody data
            mycursor.execute(query_for_biophysical, (pdb_id,))
        elif antigen_selected:
            # If only antigen is selected, filter by antigen
            mycursor.execute(query_for_biophysical_antigen, (pdb_id,))
        elif antibody_selected:
            # If only antibody is selected, filter by antibody
            mycursor.execute(query_for_biophysical_antibody, (pdb_id,))

        query = mycursor.fetchall()
        biophysical_properties_column_names = [i[0] for i in mycursor.description]

    # Modify and organize the biophysical data
        for result in query:
            result_list = list(result)
            phi_value = result_list[10]
            psi_value = result_list[11]
            omega_value = result_list[12]
            chi_value = result_list[13]

            if phi_value is not None:
                result_list[10] = round(phi_value, 2)
            if psi_value is not None:
                result_list[11] = round(psi_value, 2)
            if omega_value is not None:
                result_list[12] = round(omega_value, 2)
            if chi_value is not None:
                result_list[13] = round(chi_value, 2)

        # Store the result in the biophysical_data dictionary
            if pdb_id in biophysical_data:
                biophysical_data[pdb_id].append(result_list)
            else:
                biophysical_data[pdb_id] = [result_list]

# Fetch CDR images
    cdr_images = {}
    for pdb_id in pdb_ids:
        image_filename = f"{pdb_id}-cdr.png"
        cdr_image_url = url_for('static', filename=image_filename)
        cdr_images[pdb_id] = cdr_image_url

    # Render the template with organized data
    return render_template('results.html', biophysical_data=biophysical_data, cdr_data=cdr_data,
                        biophysical_properties_column_names=biophysical_properties_column_names,
                        cdr_images=cdr_images)

@app.route('/', methods = ["GET", "POST"])
def homepage():
    return render_template('search_form.html') 
@app.route('/FoldXresults', methods = ["GET", "POST"])
def FoldX():
    return " Redirected to this website for FoldX results "
@app.route('/About')
def about():
    return render_template('about.html')
@app.route('/documentation-help')
def doc():
    return render_template('documentation.html')

if __name__ == '__main__':
    app.run(debug=True)





#CHUNK 0 ~ below's source: https://courses.prettyprinted.com/courses/1016334/lectures/20934050
#CHUNK 1 source : https://www.digitalocean.com/community/tutorials/how-to-use-an-sqlite-database-in-a-flask-application
#CHUNK 2 source : https://code-boxx.com/search-results-python-flask/
#CHUNK 4 source : https://stackoverflow.com/questions/61059678/reading-blob-from-database-without-saving-to-disk-in-python/61061587#61061587
# Related to chunk 4 ^^ : https://stackoverflow.com/questions/63340686/render-blob-from-sqlite-server-in-html-with-flask-python
#CHUNK 5 source: https://stackoverflow.com/questions/31358578/display-image-stored-as-binary-blob-in-template
#SQL Tutorial Link: https://www.tutorialspoint.com/sqlite/sqlite_using_autoincrement.htm
# FLASK Checkbox value code: https://stackoverflow.com/questions/31859903/get-the-value-of-a-checkbox-in-flask
# Possible Source: https://blog.miguelgrinberg.com/post/beautiful-interactive-tables-for-your-flask-templates
# JMOL tutorial < to try 2.5.23 > :  http://www.chm.bris.ac.uk/jmol/jmol-7/doc/JmolAppletGuide.html
# JMOl on webpage tutorial : https://www.youtube.com/watch?v=sIr-aeRCXPI
# JMOL display options scripting : https://earth.callutheran.edu/Academic_Programs/Departments/BioDev/omm/jsmol/scripting/molmast.htm#intro
