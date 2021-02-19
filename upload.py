@app.route(BASE_URL + 'file/upload', methods=['GET', 'POST'])
@token_required
def flask_encryptFile(current_user):
	con = open_connection()
	if 'folder_id' in request.headers: folder_uuid = request.headers['folder_id']
	else: folder_uuid = ''
	if 'folder_name' in request.headers: folder_name = request.headers['folder_name']
	else: folder_name = ''
	if request.method == 'POST':
		if 'file' not in request.files:
			print('No file provided')
			return jsonify({'message': 'no file provided!'})
		file = request.files['file']
		if file.filename == '':
			return jsonify({'message': 'no selected file!'})
		if file:
			print('Processing file...')
			filename = secure_filename(file.filename)
			uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(uploaded_file)
			encryptFile(uploaded_file, current_user['email'])
			print('File encrypted')
			file_size = os.path.getsize(uploaded_file)
			file_uuid = uuid.uuid4()
			extension = os.path.splitext(filename)[1]
			try:
				query = 'insert into files (file_uuid, file_name, file_extension, file_owner, folder_name, folder_uuid) values ("{0}","{1}","{2}","{3}","{4}","{5}")'.format(file_uuid, filename, extension, current_user['email'], folder_name, folder_uuid)
				cur = con.cursor()
				cur.execute(query)
				con.commit()
				cur.close()
				print('File information saved to database.')
			
			except Exception as error:
				print(error)
				
			print('File size (bytes): ' + str(file_size))
			
			with open(uploaded_file, "rb") as upload_file:
				print('Uploading to object storage...')
				minioClient.put_object('adaptivecloud', str(file_uuid) + str(extension), upload_file, file_size)
			os.remove(uploaded_file)
			return jsonify({'message': '200'})
