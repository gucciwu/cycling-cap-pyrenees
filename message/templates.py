from entry.settings import SITE

site_root = SITE.get('root', 'http://pyrenees.cycling-cap.cn/')

REGISTER_VERIFY_CODE = {
    "title": "Welcome to register Flex Travels",
    "content": "<p><strong>Dear Ms./Mr.,</strong></p>"
               "<p>Thanks for register Pyrenees!</p>"
               "<p>Please click</p>"
               "<p><strong>"
               "<a href='" + site_root + "#/user/active?code=$active_code&email=$email' target='_blank'>"
                                         "<button>here</button></a></strong></p>"
               "<p>to active you account.</p>",
}
