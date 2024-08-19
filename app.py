from flask import Flask, request, render_template, redirect, flash, session, make_response
from surveys import Question, surveys, Survey, satisfaction_survey, personality_quiz
from random import choices

CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'
responses = []

app = Flask(__name__)

app.config['SECRET_KEY'] = "dntKnow"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#       MAKING ROUTES
@app.route('/')
def show_survey():
    ''' Show survey to enduser'''

    return  render_template('pick_survey.html', surveys=surveys)

@app.route('/', methods=['POST'])
def Home_page():
    '''choose a survey'''
    title = satisfaction_survey.title
    instruction = satisfaction_survey.instructions

    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        
        return "<h1> You have completed the survey. Thank You! </h1>"
    
    survey_id = request.form['survey_code']
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template('start_survey.html',title=title, givenInstr=instruction)

@app.route('/start', methods=['POST'])
def start_survey():
    ''' Starts the survey '''
    session[RESPONSES_KEY] = []

    return redirect('/questions/0')


@app.route('/questions/<int:q_num>')
def questions(q_num):
    '''Show questions'''

    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):
        # Accessing questions without starting it.

        return redirect('/')
    
    if (len(responses)) == len(satisfaction_survey.questions):
        # If all questions are complete. Get a completion message.

        return redirect('/complete')
    
    if(len(responses) != q_num):
        # Answerin out of order
        flash(f'Invalid question number!: {q_num}.')

        return redirect(f'/questions/{len(responses)}')
    
    # if q_num >= len(satisfaction_survey.questions):
    #     return redirect('/complete')
    
    questions = satisfaction_survey.questions[q_num]

    return render_template('question.html', question=questions, q_num=q_num)


@app.route('/answers',methods=['POST'])
def handle_question():
    '''Get the question number form and its answer,also redirect to the next question '''

    ans = request.form['answer']
    text = request.form.get('text', '')

        # Stores answers in the sesssion
    responses = session[RESPONSES_KEY]  
    responses.append({'ans': ans, 'text': text})

    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]
   
        # All questions answered! Redirect to complete page.
    if (len(responses) == len(satisfaction_survey.questions)):
        return redirect('/complete')
    else:
        return redirect(f'/questions/{len(responses)}')
    
    
@app.route('/complete')
def complete():
    '''Returns list response and a thank you note'''

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("completion.html",
                           survey=survey,
                           responses=responses)

    # Set cookie noting this survey is done so they can't re-do it
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
