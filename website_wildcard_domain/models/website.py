# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, http
from odoo.http import request
from odoo.tools.translate import _
from werkzeug import urls

logger = logging.getLogger(__name__)


class Website(models.Model):

    _inherit = "website"

    # Overridden:
    @tools.cache('domain_name', 'country_id', 'fallback')
    @api.model
    def _get_current_website_id(self, domain_name, country_id, fallback=True):
        """Get the current website id.

        First find all the websites for which the configured `domain` (after
        ignoring a potential scheme) is equal to the given
        `domain_name`. If there is only one result, return it immediately.

        If there are no website found for the given `domain_name`, either
        fallback to the first found website (no matter its `domain`) or return
        False depending on the `fallback` parameter.

        If there are multiple websites for the same `domain_name`, we need to
        filter them out by country. We return the first found website matching
        the given `country_id`. If no found website matching `domain_name`
        corresponds to the given `country_id`, the first found website for
        `domain_name` will be returned (no matter its country).

        (extended) If a wildcard domain is set, then it filters website by matching namespace,
        thus allowing to link several sub-domains associated to same Website.

        :param domain_name: the domain for which we want the website.
            In regard to the `url_parse` method, only the `netloc` part should
            be given here, no `scheme`.
        :type domain_name: string

        :param country_id: id of the country for which we want the website
        :type country_id: int

        :param fallback: if True and no website is found for the specificed
            `domain_name`, return the first website (without filtering them)
        :type fallback: bool

        :return: id of the found website, or False if no website is found and
            `fallback` is False
        :rtype: int or False

        :raises: if `fallback` is True but no website at all is found
        """
        def _remove_port(domain_name):
            return (domain_name or '').split(':')[0]

        def _filter_domain(website, domain_name, ignore_port=False):
            """Ignore `scheme` from the `domain`, just match the `netloc` which
            is host:port in the version of `url_parse` we use."""
            # Here we add http:// to the domain if it's not set because
            # `url_parse` expects it to be set to correctly return the `netloc`.
            website_domain = urls.url_parse(website._get_http_domain()).netloc
            if ignore_port:
                website_domain = _remove_port(website_domain)
                domain_name = _remove_port(domain_name)
            return website_domain.lower() == (domain_name or '').lower()

        # Sort on country_group_ids so that we fall back on a generic website:
        # websites with empty country_group_ids will be first.
        found_websites = self.search([('domain', 'ilike', _remove_port(domain_name))]).sorted('country_group_ids')
        # Filter for the exact domain (to filter out potential subdomains) due
        # to the use of ilike.
        websites = found_websites.filtered(lambda w: _filter_domain(w, domain_name))
        # If there is no domain matching for the given port, ignore the port.
        websites = websites or found_websites.filtered(lambda w: _filter_domain(w, domain_name, ignore_port=True))

        # lets try wildcard.
        if not websites:
            d1 = _remove_port(domain_name).split('.')
            wildcard_domain = '*.%s.%s' % (d1[len(d1) - 2], d1[len(d1) - 1])

            found_websites = self.search([('domain', 'ilike', wildcard_domain)]).sorted('country_group_ids')
            websites = websites or found_websites.filtered(lambda w: _filter_domain(w, wildcard_domain, ignore_port=True))

        if not websites:
            if not fallback:
                return False
            return self.search([], limit=1).id
        elif len(websites) == 1:
            return websites.id
        else:  # > 1 website with the same domain
            country_specific_websites = websites.filtered(lambda website: country_id in website.country_group_ids.mapped('country_ids').ids)
            return country_specific_websites[0].id if country_specific_websites else websites[0].id
