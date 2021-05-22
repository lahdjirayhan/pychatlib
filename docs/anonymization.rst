Notes on anonymization
======================

Why anonymize?

To make it more comfortable and convenient to e.g. perform data analysis on chat data where it may be
better to not reveal any actual usernames.

While this package can anonymize the chat data, I have to admit (and **warn** you) that it is not perfect.
It only anonymizes username mentions, e.g. something that starts with an @ sign, and certainly **can not**
anonymize names (either proper or nickname), locations, etc. that are uttered in a chat; because it can't
tell.

The general process of anonymization is:

1. Chat data is read into Python in non-anonymous manner. This is to obtain known usernames as many as possible
   from the sender list.
2. Every record (message and other non-chat events) are searched for usernames. If a known username is found, It
   is replaced by an integer ID. If an unknown username is found (i.e. something resembling a username, but not
   actually contained in the sender list), it is replaced by something else.

Why bother anonymizing unknown usernames?

I'm thinking there could be a reasonable edge case where a person (let's say @Joe) is in a group chat. They
never sent any message and never triggered any event, thus @Joe is not listed in sender list (i.e. unknown).
But it's still possible that other group members try to tag/mention him, thus revealing his username in a message.

Another (positive, I think) side effect of anonymizing unknown username is that other social media
accounts e.g. Twitter username that happens to be uttered in a message becomes anonymized. However,
be advised that this is a side effect, not the actual intention of doing an anonymization, so the behavior
might be a little more unexpected.