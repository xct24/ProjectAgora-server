import connexion
import six
import os
import requests
from tzlocal import get_localzone
from flask import Flask, send_from_directory
from exchangelib import Credentials, Account, Configuration, DELEGATE, RoomList, CalendarItem, EWSDateTime
from exchangelib.services import GetRooms
from exchangelib.items import MeetingRequest, MeetingCancellation, SEND_TO_ALL_AND_SAVE_COPY

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server import util, orm, weapp

credentials = Credentials(
    os.environ["EWS_admin_email"],
    os.environ["EWS_admin_password"])

config = Configuration(server='outlook.office365.com', credentials=credentials)

account = Account(
    primary_smtp_address='admin@agoraacademy.cn',
    credentials=credentials,
    autodiscover=False,
    config=config,
    access_type=DELEGATE
)


def miniprogram_event_post(eventPostBody):
    # 创建活动接口
    db_session = None
    if "DEVMODE" in os.environ:
        if os.environ["DEVMODE"] == "True":
            db_session = orm.init_db(os.environ["DEV_DATABASEURI"])
        else:
            db_session = orm.init_db(os.environ["DATABASEURI"])
    else:
        db_session = orm.init_db(os.environ["DATABASEURI"])
    eventPostBody_dict = connexion.request.get_json()
    sessionKey = connexion.request.headers['token']
    learner = db_session.query(orm.Learner_db).filter(orm.Learner_db.sessionKey == sessionKey).one_or_none()
    if not learner:
        db_session.remove()
        return {"message": "learner not found"}, 401
    # 自定义鉴权
    if not learner.isAdmin:
        if "initiatorDisplayName" in eventPostBody:
            db_session.remove()
            return {"message": "非管理员不可自定义发起者名称"}, 401
        initiatorDisplayName = learner.familyName + learner.givenName
    else:
        initiatorDisplayName = eventPostBody_dict["initiatorDisplayName"] if "initiatorDisplayName" in eventPostBody_dict else learner.familyName + learner.givenName
    try:
        newEvent = orm.Event_db(
            initiatorId=learner.id,
            initiatorDisplayName=initiatorDisplayName,
            eventInfo=eventPostBody_dict["eventInfo"],
            invitee=eventPostBody_dict["invitee"],
            thumbnail=eventPostBody_dict["thumbnail"]
        )
        db_session.add(newEvent)
        db_session.commit()
        newPushMessage = orm.PushMessage_db(
            messageType="Event",
            entityId=newEvent.id,
            senderId=learner.id,
            senderDisplayName=initiatorDisplayName,
            recipients=eventPostBody_dict["invitee"],
            rsvp=[],
            sentTime=account.default_timezone.localize(EWSDateTime.now()).ewsformat(),
            modifiedTime=account.default_timezone.localize(EWSDateTime.now()).ewsformat(),
            expireTime=eventPostBody_dict["expireTime"],
            thumbnail=eventPostBody_dict["thumbnail"],
            content=eventPostBody_dict["content"]
        )
        db_session.add(newPushMessage)
        db_session.commit()
        # TODO: 这里应当添加Microsoft Graph API为initiator添加appointment并发送至recipients
    except Exception as e:
        db_session.remove()
        return {'error': str(e)}, 400
    response = {"pushMessage_id": newPushMessage.id, "event_id": newEvent.id}
    db_session.remove()
    return response, 201
