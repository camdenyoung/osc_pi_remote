from flask import Flask, render_template_string, request, redirect
import configparser

app = Flask(__name__)
CONFIG_FILE = 'config.ini'


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


@app.route('/', methods=['GET', 'POST'])
def config_page():
    config = load_config()

    if request.method == 'POST':
        config['server']['host'] = request.form['host']
        config['server']['port'] = request.form['port']
        config['server']['retry_delay'] = request.form['retry_delay']
        config['buttons']['btn1_on_path'] = request.form['btn1_on_path']
        config['buttons']['btn1_on_value'] = request.form['btn1_on_value']
        config['buttons']['btn1_off_path'] = request.form['btn1_off_path']
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        return redirect('/')

    host = config['server'].get('host', '127.0.0.1')
    port = config['server'].get('port', '5000')
    retry_delay = config['server'].get('retry_delay', '30')
    btn1_on_path = config['buttons'].get('btn1_on_path', '/cue/1/start')
    btn1_on_value = config['buttons'].get('btn1_on_value', '1')
    btn1_off_path = config['buttons'].get('btn1_off_path')

    print(btn1_on_path)

    return render_template_string('''
        <h1>OSC Remote Setup</h1>
        <form method="post">
        <h2>Edit Server Configuration</h2>
            Host: <input type="text" name="host" value="{{ host }}"><br>
            Port: <input type="text" name="port" value="{{ port }}"><br>
            Retry Delay: <input type="text" name="retry_delay" value="{{ retry_delay }}"><br>
            <input type="submit" value="Save">

        <h2>Edit OSC Messages</h2>
         
            Button 1 On Path: <input type="text" name="btn1_on_path" value="{{ btn1_on_path }}"><br>
            Button 1 On Value: <input type="text" name="btn1_on_value" value="{{ btn1_on_value }}"><br>
            Button 1 Off Path: <input type="text" name="btn1_off_path" value="{{ btn1_off_path }}"><br>
            <input type="submit" value="Save">
        </form>                                 
    ''', host=host, port=port, retry_delay=retry_delay, btn1_on_value=btn1_on_value, btn1_on_path=btn1_on_path, btn1_off_path=btn1_off_path)


if __name__ == '__main__':
    app.run(debug=True)
