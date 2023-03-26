import numpy as np
import cv2


border_coef = {
    (320, 240): 0.2,
    (1280, 720): 0.002,                    # Коэффиценты для данного разрешения
    (960.0, 720.0): 0.02,
}  


def lum_diff(frame) -> float:
    """Find luminance difference of frame

    Args:
        frame (np.ndarray): Current frame in np.array format

    Returns:
        float: luminance difference value
    """
    
    hist, bins = np.histogram(frame)
    width = frame.shape[1]
    height = frame.shape[0]
    border = (width * height) * border_coef[(width, height)]


    hlist = []
    for h in hist:
        if sum(hlist) <= border:
            hlist.append(h)

    lum_diff = sum(hlist) / sum(bins)

    return lum_diff


def get_epilepthic_risk(chunk, framerate) -> float:
    """Target value of the probability of epileptic frames in a chunk (Average value)

    Args:
        chunk (List[np.ndarray]): Array of frames (default 5)
        framerate (int): frame frequency (FPS)

    Returns:
        float: average risk in chunk
    """
    
    epilepthic_risk_list = []

    for i, _ in enumerate(chunk):
        try:
            previous_frame = chunk[i]
            current_frame = chunk[i + 1]


            current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            previous_frame_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

            difference_frame = cv2.absdiff(previous_frame_gray, current_frame_gray)

            negative_frame = previous_frame_gray - difference_frame
            positive_frame = current_frame_gray + difference_frame

            positive_luminance = int(abs(lum_diff(positive_frame)))
            negative_luminance = int(abs(lum_diff(negative_frame)))

            epilepthic_risk = (positive_luminance - negative_luminance) / framerate

            epilepthic_risk_list.append(epilepthic_risk)
        except:
            pass

    try:
        avg_risk = sum(epilepthic_risk_list) / len(epilepthic_risk_list)
    except:
        avg_risk = 0

    return avg_risk
