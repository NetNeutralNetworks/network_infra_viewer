def render_config_scores(security, reliability, management):
    if security:
        if security < 70:
            security = f"""<span class="label label-danger">Security: {security:.1f}</span>"""
        elif security < 90:
            security = f"""<span class="label label-warning">Security: {security:.1f}</span>"""
        else:
            security = f"""<span class="label label-success">Security: {security:.1f}</span>"""
    else:
        security=''
    if reliability:
        if reliability < 70:
            reliability = f"""<span class="label label-danger">Reliability: {reliability:.1f}</span>"""
        elif reliability < 90:
            reliability = f"""<span class="label label-warning">Reliability: {reliability:.1f}</span>"""
        else:
            reliability = f"""<span class="label label-success">Reliability: {reliability:.1f}</span>"""
    else:
        reliability=''

    if management:
        if management < 70:
            management = f"""<span class="label label-danger">Management: {management:.1f}</span>"""
        elif management < 90:
            management = f"""<span class="label label-warning">Management: {management:.1f}</span>"""
        else:
            management = f"""<span class="label label-success">Management: {management:.1f}</span>"""
    else:
        management=''

    return security, reliability, management

def render_positive_negative(security, reliability, management):
    if security < 0:
        security = f"""<span class="label label-danger">Security: {security:.1f}</span>"""
    else:
        security = f"""<span class="label label-success">Security: {security:.1f}</span>"""

    if reliability < 0:
        reliability = f"""<span class="label label-danger">Reliability: {reliability:.1f}</span>"""
    else:
        reliability = f"""<span class="label label-success">Reliability: {reliability:.1f}</span>"""

    if management < 0:
        management = f"""<span class="label label-danger">Management: {management:.1f}</span>"""
    else:
        management = f"""<span class="label label-success">Management: {management:.1f}</span>"""

    return security, reliability, management