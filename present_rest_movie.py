# Very basic script to use PsychoPy to show video in resting task while in the
# scanner
#
# GS, 12/2018

from psychopy import visual, core, event

win = visual.Window(fullscr=True, noGUI=True)
win.mouseVisible = False

msg = visual.TextStim(win, text=u"Waiting for scanner...")
msg.draw()
win.flip()

event.waitKeys(keyList=["escape", 't'], clearEvents=True)

routineTimer = core.CountdownTimer() 

mov = visual.MovieStim3(win, filename='/Users/sudregp/Downloads/test.mp4',
                        noAudio=True, flipVert=False,
                        units='norm', pos=(0, 0), size=(2, 2))

# change this to set the duration of the experiment
routineTimer.add(10)#mov.duration)

mov.play()

while routineTimer.getTime() > 0:
    win.flip()
    mov.draw()  # draw the current frame (automagically determined)
    if event.getKeys(keyList=["escape"]):
        core.quit()

core.wait(1)
win.close()