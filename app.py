import os
import gc
import urllib
from flask import Flask, render_template, url_for, request, render_template_string
from Solve_Sudoku import *
from OpenCV_Sudoku import *
from NumberExtractor_Sudoku import *
import time
import warnings
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from keras.models import model_from_json
warnings.filterwarnings('ignore')


app = Flask(__name__)
CORS(app)

drive_path = os.getcwd()

app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.png']
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

app.config['UPLOAD_FOLDER'] = os.path.join(drive_path,'uploads')

model_path_json = 'models/model.json'
model_path_weight = 'models/model.h5'

json_file = open(os.path.join(drive_path,model_path_json), 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights(os.path.join(drive_path,model_path_weight))
print("Loaded saved model from disk.")

# @app.route('/')
# def hello_world():
#     return render_template_string("Hello World !")

@app.route('/')
def home():
    return render_template('sudoku.html', data={}, sudoku_message="", image_message="")


@app.route('/solveSudoku',methods=['POST'])
def solveSudoku():
    start = time.time()
    end = 0
    print('\n\n')
    print('*'*25,"Initial Sudoku Grid",'*'*25)
    print('\n\n')
    
    grid = [ [ 0 for i in range(9)] for row in range(9) ]
    
    valid_input=False
    
    for i in range(9):
        for j in range(9):
            value = request.form['grid'+str(i)+str(j)]
            if len(value.strip()) > 0:
                valid_input=True
                grid[i][j] = int(value.strip())
    
    init_grid = grid.copy()
    
    print_board(grid)
    
    valid_config=False
    
    if isValidConfig(grid,9):
    
        valid_config=True
        
        grid = np.array(grid)
        
        print('\n\n')
        print('*'*25,"Solving Sudoku Grid",'*'*25)
        print('\n\n')
        
        solve_sudoku(grid)
        print_board(grid)
        sudoku_message = '';
        end = time.time()
    
    print('valid_input - ',valid_input)
    print('valid_config - ',valid_config)
    
    if verify_board(grid) and valid_input and valid_config:
        data = {}
        for i in range(9):
            for j in range(9):
                data['grid'+str(i)+str(j)] = grid[i][j]
        sudoku_message = "Solved in "+str(round(end-start,4))+" seconds !!"        
    else:
        data = {}
        for i in range(9):
            for j in range(9):
                if int(init_grid[i][j]) != 0:
                    data['grid'+str(i)+str(j)] = init_grid[i][j]
                else:
                    data['grid'+str(i)+str(j)] = ' '
        sudoku_message = "Not a valid Board!!"
    
    print('\n\n')
    print('*'*25,"Solved",'*'*25)
    print('\n\n')
    
    del grid
    del init_grid
    del valid_config
    del start
    del end
    del valid_input
    gc.collect()
    
    return render_template('sudoku.html', data=data, sudoku_message=sudoku_message, image_message="")

@app.route('/readImage',methods=['POST'])
def readImage():
    start = time.time()
    file = request.files['file']
    imagePath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(imagePath)
    print(imagePath)
    img = cv2.imread(imagePath)
    print(img.shape)
    print('\n\n')
    print('*'*25,"Detecting Image",'*'*25)
    print('\n\n')

    image = extract_sudoku(imagePath)
    grid = extract_number(loaded_model,image)
    init_grid = grid.copy()
    
    data = {}
    
    for i in range(9):
        for j in range(9):
            if int(grid[i][j]) != 0:
                data['grid'+str(i)+str(j)] = grid[i][j]
    
    end = time.time()
    image_message = "Detected in "+str(round(end-start,4))+" seconds !!"
    
    os.remove(imagePath)
    del file
    del imagePath
    del img
    del image
    del grid
    del init_grid
    del start
    del end
    gc.collect()
    
    return render_template('sudoku.html', data=data, sudoku_message="", image_message=image_message)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 7860
    print("#"*50,"--Application Serving Now--","#"*50)
    # app.run(host=host,port=port)
    app_serve = WSGIServer((host,port),app)
    app_serve.serve_forever()
