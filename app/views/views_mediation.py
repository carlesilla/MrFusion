from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.shortcuts import render, redirect

from app import mediator
from app.models import Chat, ChatHistory, ConflictInfo, Question, UserProfile, Context

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import datetime
import json



def send_message_to_chat(chat_uuid, sender_user_id, chat_message):
    message = {
                "type": "chat.mediator",
                "chat_message": chat_message,
                "sender_user_id": sender_user_id,
    }
        
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f'chat_{chat_uuid}',message)



@login_required
def request_mediation(request, uuid):
    if request.method == "POST":
        chat = Chat.objects.get(uuid=uuid)
        if chat.is_caucus == True:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.initial_interview_concluded == False:
                # Intro message
                if ChatHistory.objects.filter(chat=chat, is_llm=True).count() == 0:
                    message = f"Hi {request.user.first_name}, this chat is only so that you and I can talk privately. \
                    Next I am going to ask you some questions to better understand the situation."
                    ChatHistory.objects.create(chat=chat, message=message, is_llm=True, is_relevant=False)

                    # Check if conflict description is done
                    if not ConflictInfo.objects.filter(created_by=request.user).exists():
                        message = f"But before continuing, could you please complete the description of the conflict \
                        from your point of view? (click the feather icon)"
                        ChatHistory.objects.create(chat=chat, message=message, is_llm=True, is_relevant=False)
                        return redirect("/chat/" + uuid)
                
                # If you haven't done so yet, generate questions for the user
                if Question.objects.filter(question_for=request.user).count() == 0:
                    # Parties in conflict
                    user_profiles = UserProfile.objects.filter(is_party=True)
                    parties = []
                    for user_profile in user_profiles:
                        parties.append(user_profile.user.first_name)
                    parties = " and ".join(parties)
                    party = request.user.first_name
                    conflict_info = ConflictInfo.objects.filter(created_by=request.user).first()
                    conflict_description = conflict_info.description
                    try:
                        questions = mediator.generate_questions(party, parties, conflict_description)
                        for question in questions:
                            Question.objects.create(question=question.get("question"), question_for=request.user)

                    except Exception as e:
                        print("Error!!", str(e))
                
                # Check if all questions have been answered
                unanswered_questions = Question.objects.filter(question_for=request.user, answer="")
                if unanswered_questions.count() > 0:
                    chat_history = ChatHistory.objects.filter(chat=chat, is_relevant=True)
                    for unanswered_question in unanswered_questions:
                        answer = mediator.check_if_answered(unanswered_question.question, chat_history)
                        if answer != "not found":
                            unanswered_question.answer = answer
                            unanswered_question.save()


                    unanswered_question = Question.objects.filter(question_for=request.user, answer="").first()
                    if unanswered_question:
                        ChatHistory.objects.create(chat=chat, message=unanswered_question.question, is_llm=True)
                        return redirect("/chat/" + uuid)
                else:
                    # Review the questions and answers given, and decide if we have to ask more questions
                    # PENDING
                    pass

                
                # Initial one-to-one interview concluded
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.initial_interview_concluded = True
                user_profile.save()

                # Say that everything is clear and that we can proceed to talk to the rest to find a solution to the conflict
                # Send a message to indicate that the initial interview has concluded
                message = f"""Thanks {request.user.first_name}, with all this information I am now clear what the problem is. \
                We can proceed to talk with the rest to find a solution to the conflict. \
                You already know that you can use this chat to discuss anything with me in private."""
                ChatHistory.objects.create(chat=chat, message=message, is_llm=True)
                return redirect("/chat/" + uuid)
            else:
                # The initial one-to-one interview is already done, let's try to answer as best we can based on the chat history.
                user_profiles = UserProfile.objects.filter(is_party=True)
                parties = []
                for user_profile in user_profiles:
                    parties.append(user_profile.user.first_name)
                parties = " and ".join(parties)
                name = request.user.first_name
                conflict_info = ConflictInfo.objects.filter(created_by=request.user).first()
                conflict_description = conflict_info.description
                chat_history = ChatHistory.objects.filter(chat=chat, is_relevant=True)
                answer = mediator.generate_caucus_answer(name, parties, conflict_description, chat_history)
                if answer is not None:
                    ChatHistory.objects.create(chat=chat, message=answer, is_llm=True)
                    return redirect("/chat/" + uuid)

        else:
            # Parties in conflict in this particular chat
            user_profiles = UserProfile.objects.filter(is_party=True)
            parties = []
            chat_members = chat.members.all()
            for user_profile in user_profiles:
                if user_profile.user in chat_members:
                    parties.append(user_profile.user.first_name)
            parties = " and ".join(parties)

            # Let's do a recap with the conflict descriptions of each member of the Chat
            if Context.objects.filter(chat=chat, context_type="conflict_info").exists():
                conflict_info_summary = Context.objects.filter(chat=chat, context_type="conflict_info").first().data
            else:
                conflict_infos = ConflictInfo.objects.all()
                chat_members_conflict_infos = []
                for conflict_info in conflict_infos:
                    if conflict_info.created_by in chat_members:
                        chat_members_conflict_infos.append(conflict_info)
                conflict_info_summary = mediator.merge_conflict_infos(chat_members_conflict_infos)
                Context.objects.create(
                    chat = chat,
                    context_type = "conflict_info",
                    data = conflict_info_summary
                )

            # Chat history
            chat_history = ChatHistory.objects.filter(chat=chat, is_relevant=True).order_by("created_at")
            if not ChatHistory.objects.filter(chat=chat, is_llm=True).exists():              
                answer = mediator.generate_multiparty_intro(conflict_info_summary, parties, chat.description, chat_history)
            else:
                # Let's check if there is already any agreement in the message history
                agreement = mediator.check_if_agreement(conflict_info_summary, parties, chat_history)
                agreement = json.loads(agreement)
                if agreement["is_agreement"] == "no":
                    answer = mediator.generate_multiparty_answer(conflict_info_summary, parties, chat.description, chat_history)
                else:
                    if Context.objects.filter(chat=chat, context_type="agreement").exists():
                        context_agreement = Context.objects.filter(chat=chat, context_type="agreement").first()
                        context_agreement.data = agreement["agreement_description"]
                        context_agreement.save()
                    else:
                        Context.objects.create(
                            chat=chat,
                            context_type = "agreement",
                            data = agreement["agreement_description"]
                        )
                    answer = mediator.generate_multiparty_closing(conflict_info_summary, parties, agreement)
            
            if answer is not None:
                send_message_to_chat(uuid, request.user.id, answer)

    return redirect("/chat/" + uuid)


@login_required
def generate_user_answer(request, uuid):
    if request.method == "POST":
        name = request.user.first_name
        conflict_info = ConflictInfo.objects.filter(created_by=request.user).first()
        conflict_description = conflict_info.description
        chat = Chat.objects.get(uuid=uuid)
        chat_history = ChatHistory.objects.filter(chat=chat, is_relevant=True).order_by("created_at")
        answer = mediator.generate_user_answer(name, conflict_description, chat_history)

        return HttpResponse(f'<div class="d-none" id="generated_text">{answer}</div>')

