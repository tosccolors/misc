# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Popup on mail error",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Show users a popup for mail delivery errors",
    "author": "The Open Source Company",
    "website": "http://www.tosc.nl",
    "category": "Extra Tools",
    "depends": [
        "mail",
        "web_notify",
    ],
    "installable": True,
    "data": [
        "security/mail_delivery_error_popup.xml",
    ],
}
