import textwrap


class MessageLog:
    def __init__(self, width, height):
        self.messages = []
        self.width = width
        self.height = height

    def add(self, message, turn):
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append((message, turn))
