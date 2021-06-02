import uuid
from django.db import models
from django.db.models.base import Model
from django.db.models.constraints import UniqueConstraint


class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options'
    )
    description = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.description

    def check_if_user_can_vote(self, session_id: str):
        return not VotesControl.objects.filter(
            session_id=session_id,
            poll=self.poll
        ).exists()

    def register_vote(self, session_id: str):
        self.votes += 1
        self.save()
        #VotesControl.objects.create(
        #    session_id=session_id,
        #    poll=self.poll
        #)
        return True


class VotesControl(models.Model):
    """
    Model que faz o controle de "quem votou em quê".
    Ela garante que cada sessão de usuário possa votar somente uma vez em
    cada enquete.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session_id = models.CharField(max_length=16)
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    def __str__(self) -> str:
        return f"{self.session_id} - {self.poll.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session_id', 'poll'],
                name="Voto único"
            )
        ]
