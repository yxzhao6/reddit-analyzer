from app import app # Import the Flask application instance from the app package

if __name__ == '__main__':
    # This block ensures that the Flask development server is started only when
    # this script (run.py) is executed directly (not when imported as a module).
    #
    # app.run() starts the development server:
    # - debug=True: Enables debug mode, which provides helpful error messages
    #               and automatically reloads the server when code changes.
    #               This should be False in a production environment.
    # - host='0.0.0.0': (Optional) Makes the server accessible externally.
    #                   Default is '127.0.0.1' (localhost).
    # - port=5000: (Optional) Specifies the port. Default is 5000.
    app.run(debug=True)
