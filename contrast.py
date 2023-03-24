import cv2


def edit_contrast(frame, alpha):
    adjusted = cv2.convertScaleAbs(frame, alpha=alpha)

    # for tests only
    # cv2.imshow('adjusted', adjusted)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    return adjusted
