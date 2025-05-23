from flask import Flask, render_template_string, request, redirect
import configparser
import subprocess

app = Flask(__name__)
CONFIG_FILE = 'config.ini'


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


def get_service_status(service_name):
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', service_name], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'inactive'


@app.route('/restart_service', methods=['POST'])
def restart_service():
    try:
        subprocess.run(
            ['systemctl', 'restart', 'osc_button.service'], check=True)
        print("Service restarted successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to restart service:", e)
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def config_page():
    config = load_config()

    if request.method == 'POST':
        # Server settings
        config['server']['host'] = request.form['host']
        config['server']['port'] = request.form['port']
        config['server']['retry_delay'] = request.form['retry_delay']

        # Button settings (btn1 - btn4)
        for i in range(1, 5):
            # Allow empty path
            config['buttons'][f'btn{i}_on_path'] = request.form.get(
                f'btn{i}_on_path', '')
            config['buttons'][f'btn{i}_off_path'] = request.form.get(
                f'btn{i}_off_path', '')

            # Default value to '1' if empty
            on_value = request.form.get(f'btn{i}_on_value', '').strip()
            config['buttons'][f'btn{i}_on_value'] = on_value if on_value else '1'

            off_value = request.form.get(f'btn{i}_off_value', '').strip()
            config['buttons'][f'btn{i}_off_value'] = off_value if off_value else '1'

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

        return redirect('/')

    # Load current values
    server_config = {key: config['server'].get(key, '') for key in [
        'host', 'port', 'retry_delay']}
    buttons_config = {}
    for i in range(1, 5):
        buttons_config[f'btn{i}_on_path'] = config['buttons'].get(
            f'btn{i}_on_path', '')
        buttons_config[f'btn{i}_on_value'] = config['buttons'].get(
            f'btn{i}_on_value', '1')
        buttons_config[f'btn{i}_off_path'] = config['buttons'].get(
            f'btn{i}_off_path', '')
        buttons_config[f'btn{i}_off_value'] = config['buttons'].get(
            f'btn{i}_off_value', '1')

    service_status = get_service_status('osc_button.service')

    return render_template_string('''
        <h1>OSC Remote Setup</h1>
        <p>Service Status: 
            <strong style="color: {{ 'green' if service_status == 'active' else 'red' }}">
                {{ service_status | capitalize }}
            </strong>
        </p>
        </form>
        <form method="post" action="/restart_service">
            <input type="submit" value="Restart osc_button.service">
        </form>
        <form method="post">
            <h2>Edit Server Configuration</h2>
            Host: <input type="text" name="host" value="{{ host }}"><br>
            Port: <input type="text" name="port" value="{{ port }}"><br>
            Retry Delay: <input type="text" name="retry_delay" value="{{ retry_delay }}"><br>

            <h2>Edit OSC Messages</h2>
            {% for i in range(1, 5) %}
                <h3>Button {{ i }}</h3>
                On Path: <input type="text" name="btn{{ i }}_on_path" value="{{ buttons['btn' ~ i ~ '_on_path'] }}"><br>
                On Value: <input type="number" name="btn{{ i }}_on_value" value="{{ buttons['btn' ~ i ~ '_on_value'] }}" step="0.1"><br>
                Off Path: <input type="text" name="btn{{ i }}_off_path" value="{{ buttons['btn' ~ i ~ '_off_path'] }}"><br>
                Off Value: <input type="number" name="btn{{ i }}_off_value" value="{{ buttons['btn' ~ i ~ '_off_value'] }}" step="0.1"><br>
                <br>
            {% endfor %}
            <input type="submit" value="Save">
    ''', host=server_config['host'], port=server_config['port'],
        retry_delay=server_config['retry_delay'], buttons=buttons_config, service_status=service_status)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)
