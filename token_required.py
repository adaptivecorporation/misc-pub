def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, constants.SECRET_KEY)
            con = open_connection()
            try:
                queryGetUser = 'select * from users where email = "%s";' % (data['email'])
                cur = con.cursor()
                cur.execute(queryGetUser)
                result = cur.fetchall()
            except Exception as error:
                print(error)
        except Exception as error:
            print(error)

            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(result[0], *args, **kwargs)

    return decorated
