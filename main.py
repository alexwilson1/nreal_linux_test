import cv2
import subprocess
import threading
import collections
import subprocess
import time
import numpy as np

command = "./nrealAirLinuxDriver"

input_screens_width = 1920
input_screens_height = 1080
output_screen_width = 1920
output_screen_height = 1080
num_input_screens = 2


initial_pitch_value = None
initial_roll_value = None
initial_yaw_value = None


def read_output(process, append):
    for stdout_line in iter(process.stdout.readline, ""):
        append(stdout_line)


process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    universal_newlines=True,
    cwd="/home/nrealAirLinuxDriver/build/",
)
number_of_lines = 1
q = collections.deque(maxlen=number_of_lines)
t = threading.Thread(target=read_output, args=(process, q.append))
t.daemon = True
t.start()


def get_pitch_roll_yaw(input_str):
    pitch, roll, yaw = map(
        float,
        "".join(input_str)
        .replace("Pitch:", "")
        .replace("Roll:", "")
        .replace("Yaw:", "")
        .split(";"),
    )

    return (roll, pitch, yaw)


cap = cv2.VideoCapture(
    f"ximagesrc use_damage=1 endx={num_input_screens*input_screens_width-1} ! queue ! videoconvert ! video/x-raw, format=BGR ! appsink"
)


if not cap.isOpened():
    print("Cannot capture from camera. Exiting.")
    quit()

start_time = time.time()  # start timer

while True:
    elapsed_time = time.time() - start_time  # get elapsed time
    if elapsed_time >= 10:  # if elapsed time is greater than or equal to 10 seconds
        initial_pitch_value, initial_roll_value, initial_yaw_value = get_pitch_roll_yaw(
            q
        )  # save pitch, roll, and yaw values
        print(
            "Initial values saved - Pitch: {:.2f}; Roll: {:.2f}; Yaw: {:.2f}".format(
                initial_pitch_value, initial_roll_value, initial_yaw_value
            )
        )
        break


def get_monitor_pixels(pixels_array, input_screens_width, monitor_index):
    num_monitors = pixels_array.shape[1] // input_screens_width
    if monitor_index < 0 or monitor_index >= num_monitors:
        raise ValueError(
            f"Invalid monitor index: {monitor_index}. There are {num_monitors} monitors in the array."
        )
    start_col = monitor_index * input_screens_width
    end_col = start_col + input_screens_width
    return pixels_array[:, start_col:end_col, :]


# translate from one range to another
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


user_input = input(
    "Press enter once you are looking at your (imaginary) 'leftmost' screen"
)
left_yaw_value = get_pitch_roll_yaw(q)[2]
user_input = input(
    "Press enter once you are looking at your (imaginary) 'rightmost' screen"
)
right_yaw_value = get_pitch_roll_yaw(q)[2]
# user_input = input(
#     "Press enter once you are looking above your (imaginary) 'front' screen"
# )
# up_pitch_value = get_pitch_roll_yaw(q)[0]
# user_input = input(
#     "Press enter once you are looking below your (imaginary) 'front' screen"
# )
# down_pitch_value = get_pitch_roll_yaw(q)[0]

while True:
    ret, frame = cap.read()

    if ret == False:
        break

    if "".join(q) is not None:
        try:
            pitch, roll, yaw = get_pitch_roll_yaw(q)
            # print("Pitch: {:.2f}; Roll: {:.2f}; Yaw: {:.2f}".format(pitch, roll, yaw))
            normed_yaw_angle = translate(yaw, left_yaw_value, right_yaw_value, -1, 1)
            if normed_yaw_angle > 1:
                normed_yaw_angle = 1
            if normed_yaw_angle < -1:
                normed_yaw_angle = -1

            # normed_pitch_angle = translate(
            #     pitch, down_pitch_value, up_pitch_value, -1, 1
            # )
            # if normed_pitch_angle > 1:
            #     normed_pitch_angle = 1
            # if normed_pitch_angle < -1:
            #     normed_pitch_angle = -1

            # looking left case
            if normed_yaw_angle < 0:
                img_left_mon = np.array(
                    get_monitor_pixels(frame, input_screens_width, 0)
                )
                img_center_mon = np.array(
                    get_monitor_pixels(frame, input_screens_width, 1)
                )
                sliced_img_left_mon = img_left_mon[
                    :, int((1 - abs(normed_yaw_angle)) * input_screens_width) :, :
                ]
                sliced_img_center_mon = img_center_mon[
                    :, 0 : int((1 - abs(normed_yaw_angle)) * input_screens_width), :
                ]

                img = np.concatenate(
                    (sliced_img_left_mon, sliced_img_center_mon), axis=1
                )

            # looking right case
            if normed_yaw_angle >= 0:
                img_right_mon = np.array(
                    get_monitor_pixels(frame, input_screens_width, 0)
                )
                img_center_mon = np.array(
                    get_monitor_pixels(frame, input_screens_width, 1)
                )
                sliced_img_right_mon = img_right_mon[
                    :, 0 : int(abs(normed_yaw_angle) * input_screens_width), :
                ]
                sliced_img_center_mon = img_center_mon[
                    :, int(abs(normed_yaw_angle) * input_screens_width) :, :
                ]

                img = np.concatenate(
                    (sliced_img_center_mon, sliced_img_right_mon), axis=1
                )

            # # looking up case
            # print(pitch)
            # if normed_pitch_angle > 0:
            #     # shift image down, replacing by black
            #     showing_screen = img[
            #         0 : int((1 - abs(normed_pitch_angle)) * input_screens_height), :, :
            #     ]
            #     showing_black = np.zeros(
            #         (
            #             input_screens_height
            #             - int((1 - abs(normed_pitch_angle)) * input_screens_height),
            #             input_screens_width,
            #             3,
            #         ),
            #         dtype=np.uint8,
            #     )
            #     showing_black[:, :, 2] = 0
            #     img = np.concatenate((showing_black, showing_screen), axis=0)

            # # looking down case
            # if normed_pitch_angle <= 0:
            #     # shift image up, replacing by black
            #     showing_screen = img[
            #         int(abs(normed_pitch_angle) * input_screens_height) :, :, :
            #     ]
            #     showing_black = np.zeros(
            #         (
            #             int(abs(normed_pitch_angle) * input_screens_height),
            #             input_screens_width,
            #             3,
            #         ),
            #         dtype=np.uint8,
            #     )
            #     showing_black[:, :, 2] = 0
            #     img = np.concatenate((showing_screen, showing_black), axis=0)

            capname = "cap"
            cv2.namedWindow(capname, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(
                capname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
            )
            cv2.imshow(capname, img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            cv2.moveWindow(capname, input_screens_width * num_input_screens, 0)

        except Exception as e:
            print(f"Couldn't parse imu values {e}")

    # cv2.imshow("FrameREAD", frame)


cap.release()
cv2.destroyAllWindows()
