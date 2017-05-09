from policy_engine import PolicyEngine
import time

p = PolicyEngine('noc-netmode')


@p.action
def lul():
    print('LUL')

p.run()

p.enqueue_event({
    'name': 'Web Application Attack',
    'event_data': {
        'dest_port': 53,
        'src_ip': '147.102.1.1',
        'proto': 'TCP',
        'alert': {
            'action': 'LUL'
        }
    }
})
p.enqueue_event({
    'name': 'Web Application Attack',
    'event_data': {
        'dest_port': 53,
        'src_ip': '147.103.1.1',
        'proto': 'TCP',
        'alert': {
            'action': 'LUL'
        }
    }
})

time.sleep(2)