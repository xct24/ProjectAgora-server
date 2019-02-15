import connexion
import six
import os

from swagger_server.models.project import Project  # noqa: E501
from swagger_server import util, wxLogin, orm

db_session = None
db_session = orm.init_db(os.environ["DATABASEURI"])


def project_get():  # noqa: E501
    validation_result = wxLogin.validateUser()
    if not validation_result["result"]:
        return {"error": "Failed to validate access token"}, 401
    """返回所有Project

    # noqa: E501

    :param learnerId:
    :type learnerId: int

    :rtype: List[Project]
    """
    return 'do some magic!'


def project_head():  # noqa: E501
    """返回所有Project的关键信息

    # noqa: E501


    :rtype: InlineResponse2001
    """
    return 'do some magic!'


def project_patch(learner):  # noqa: E501
    """更新一个Project

    # noqa: E501


    :rtype: InlineResponse2001
    """
    return 'do some magic!'


def project_post(project):  # noqa: E501
    """创建一个Learner

    # noqa: E501

    :param learner:
    :type learner: dict | bytes

    :rtype: InlineResponse201
    """
    validation_result = wxLogin.validateUser()
    if not validation_result["result"]:
        return {"error": "Failed to validate access token"}, 401
    if connexion.request.is_json:
        project = Project.from_dict(connexion.request.get_json())
    return {}, 201, {"Authorization": validation_result["access_token"], "refresh_token": validation_result["refresh_token"]}
