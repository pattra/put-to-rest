import pygame, os, sys, math, random, json
from pygame.locals import *
from Menu import Menu
from Menu import MenuItem

# Wraps text because python is whack

def textWrap(surface, text, rect, color, font, aa=False, bkg=None):
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1
        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        nl_index = text.find("\n")
        if nl_index != -1:
            while font.size(text[:i])[0] < rect.width and i < len(text) and i < nl_index+2:
                i += 1
        else:
             while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1

        # if we've wrapped the text, then adjust the wrap to the last word  

        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text
