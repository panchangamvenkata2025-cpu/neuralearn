import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance

mp_mesh = mp.solutions.face_mesh

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


def ear(landmarks, indices, w, h):
    pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in indices]

    A = distance.euclidean(pts[1], pts[5])
    B = distance.euclidean(pts[2], pts[4])
    C = distance.euclidean(pts[0], pts[3])

    return (A + B) / (2.0 * C)


class AttentionTracker:
    def __init__(self):
        self.mesh = mp_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    # 🔥 FIXED: now accepts FRAME (not bytes)
    def analyze(self, frame) -> dict:
        h, w = frame.shape[:2]

        res = self.mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if not res.multi_face_landmarks:
            return {
                "attention_score": 30,
                "distracted": True,
                "reason": "no_face"
            }

        lm = res.multi_face_landmarks[0].landmark

        avg_ear = (ear(lm, LEFT_EYE, w, h) + ear(lm, RIGHT_EYE, w, h)) / 2
        gaze = float(np.sqrt((lm[1].x - 0.5) ** 2 + (lm[1].y - 0.4) ** 2))

        score = 100

        if avg_ear < 0.25:
            score -= 40

        if gaze > 0.15:
            score -= int(gaze * 200)

        score = max(0, min(100, score))

        return {
            "attention_score": score,
            "distracted": score < 50,
            "ear": round(avg_ear, 3),
            "gaze": round(gaze, 3)
        }

    # 🔥 FIXED CAMERA LOOP
    def start(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return {"error": "Camera not accessible"}

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 🔥 FIX: correct function call
            result = self.analyze(frame)

            # Display score
            cv2.putText(
                frame,
                f"Attention: {result['attention_score']}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.imshow("Attention Tracker", frame)

            # ESC to exit
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        return {"message": "Camera stopped"}