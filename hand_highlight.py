
import argparse
import os
import time
import cv2
import mediapipe as mp
import numpy as np
import pickle
from collections import deque
from multiprocessing import Process, shared_memory

# optional sklearn import (used during training/prediction)
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
except Exception:
    RandomForestClassifier = None

# Import MediaPipe Tasks
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def parse_args():
    parser = argparse.ArgumentParser(description="Webcam hand detection + highlight using MediaPipe")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0)")
    parser.add_argument("--max_num_hands", type=int, default=2, help="Maximum number of hands to detect")
    parser.add_argument("--model_complexity", type=int, default=1, choices=[0, 1, 2], help="Model complexity (0,1,2) - note: Tasks API only supports full model")
    parser.add_argument("--min_detection_confidence", type=float, default=0.5)
    parser.add_argument("--min_tracking_confidence", type=float, default=0.5)
    parser.add_argument("--record", type=str, default=None, help="Record samples for a given LABEL (single char/word). Press 's' to save a sample")
    parser.add_argument("--train", action="store_true", help="Train a classifier from recorded samples (dataset.csv -> model.pkl)")
    parser.add_argument("--model_path", type=str, default="modelnew.pkl", help="Path to save/load trained model")
    parser.add_argument("--two_hands", action="store_true", help="Use concatenated left+right hand features (2x42 floats) for recording/training/prediction")
    return parser.parse_args()


def hand_main():
    shm = shared_memory.SharedMemory(name="ai_output", create=True, size=20)
    shm_cords = shared_memory.SharedMemory(name="cords", create=True, size=168)

    args = parse_args()

    # Create shared memory for inter-process communication
    shm.buf[:20] = b'\x00' * 20  # Initialize with null bytes
    shm_cords.buf[:168] = b'\x00' * 168  # Initialize hand coordinates (21 landmarks * 2 coords * 4 bytes)

    # Initialize MediaPipe Tasks Hand Landmarker
    model_path = "hand_landmarker.task"  # Download from https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model not found at {model_path}")
        print(f"Download the Hand Landmarker model from:")
        print(f"https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker")
        print(f"And save it as 'hand_landmarker.task' in the current directory")
        return

    try:
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=args.max_num_hands,
            min_hand_detection_confidence=args.min_detection_confidence,
            min_hand_presence_confidence=args.min_tracking_confidence,
            min_tracking_confidence=args.min_tracking_confidence,
        )
        detector = vision.HandLandmarker.create_from_options(options)
    except Exception as e:
        print(f"ERROR: Failed to     create hand detector: {e}")
        return

    cap = cv2.VideoCapture(args.camera)

    # Set resolution to 1920x1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if not cap.isOpened():
        print(f"Cannot open camera {args.camera}")
        return

    # Get actual resolution (camera might not support exactly 1920x1080)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera resolution: {width}x{height}")

    

    # If training requested, we'll collect features and train after the loop

    # Prediction smoothing
    # Prediction smoothing
    pred_queue = deque(maxlen=8)
    

    # Prediction timing tracking
    last_prediction = None
    prediction_start_time = None
    prediction_duration = 1.0  # seconds required for stable prediction

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Flip for a selfie-view and convert to RGB
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Detect hands
        try:
            results = detector.detect(mp_image)
        except Exception as e:
            print(f"Detection error: {e}")
            results = None

        # Build per-frame features for single or two-hand mode
        current_feature = None

        # helper: convert MediaPipe hand_landmarks to a 42-float vector (x, y only)
        def landmarks_to_vector(hl):
            v = []
            for lm in hl:
                v.extend([lm.x, lm.y])
            return v

        left_vec = None
        right_vec = None
        single_hand_vec = None
        
        if results and results.hand_landmarks:
            for i, hand_landmarks in enumerate(results.hand_landmarks):
                # Draw landmarks
                pts = []
                for lm in hand_landmarks:
                    x_px = int(lm.x * width)
                    y_px = int(lm.y * height)
                    pts.append((x_px, y_px))

                pts_np = np.array(pts, dtype=np.int32)

                # Draw hand connections manually
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),  # thumb
                    (0, 5), (5, 6), (6, 7), (7, 8),  # index
                    (0, 9), (9, 10), (10, 11), (11, 12),  # middle
                    (0, 13), (13, 14), (14, 15), (15, 16),  # ring
                    (0, 17), (17, 18), (18, 19), (19, 20),  # pinky
                    (5, 9), (9, 13), (13, 17)  # palm
                ]
                for start, end in connections:
                    if start < len(pts) and end < len(pts):
                        cv2.line(frame, pts[start], pts[end], (255, 255, 255), 2)
                
                # Draw joints
                for pt in pts:
                    cv2.circle(frame, pt, 2, (255, 255, 255), -1)

                vec = landmarks_to_vector(hand_landmarks)
                
                # Write coordinates to shared memory
                coords_bytes = np.array(vec, dtype=np.float32).tobytes()
                shm_cords.buf[:len(coords_bytes)] = coords_bytes
                
                single_hand_vec = vec  # last-hand fallback

                # Determine handedness
                label = None
                if results.handedness and len(results.handedness) > i:
                    classification = results.handedness[i]
                    if classification and len(classification) > 0:
                        label = classification[0].category_name.lower()

                if label:
                    if 'left' in label:
                        left_vec = vec
                    elif 'right' in label:
                        right_vec = vec

            # Build combined feature when two_hands enabled
            if args.two_hands:
                zeros42 = [0.0] * 42
                left_final = left_vec if left_vec is not None else zeros42
                right_final = right_vec if right_vec is not None else zeros42
                current_feature = left_final + right_final
            else:
                current_feature = single_hand_vec

        # Recording mode: show prompt
        if args.record:
            mode_note = "(two-hands)" if args.two_hands else "(single-hand)"
            cv2.putText(frame, f"RECORD MODE {mode_note}: press 's' to save sample for '{args.record}'", (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Prediction mode: if model exists, predict and smooth
        def pred():
            nonlocal last_prediction, prediction_start_time
            model = None
            if os.path.exists(args.model_path):
                try:
                    with open(args.model_path, "rb") as f:
                        model = pickle.load(f)
                except Exception:
                    model = None

            if model is not None and current_feature is not None:
                try:
                    pred = model.predict([current_feature])[0]
                    pred_queue.append(pred)
                    if len(pred_queue) == pred_queue.maxlen:
                        smoothed_label = max(set(pred_queue), key=pred_queue.count)
                    else:
                        smoothed_label = pred

                    # Track prediction timing
                    current_time = time.time()
                    if smoothed_label != last_prediction:
                        # Prediction changed, reset timing
                        last_prediction = smoothed_label
                        prediction_start_time = current_time
                    elif prediction_start_time is not None:
                        # Check if prediction has been stable for required duration
                        if current_time - prediction_start_time >= prediction_duration:
                            # Write to file if we haven't already written this prediction
                            # Write to shared memory for Thor_detection.py
                            data = smoothed_label
                            shm.buf[:20] = bytes(data.ljust(20),'utf8')

                            # Reset timing to prevent multiple writes of same prediction
                            prediction_start_time = None

                    cv2.putText(frame, f"Prediction: {smoothed_label}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                except Exception as e:
                    print(f"Prediction error: {e}")
                    pass

        pred()

        cv2.imshow("MediaPipe Hands - Highlight", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 27 or key == ord('q'):
            break

        if key == ord('s') and args.record and current_feature is not None:
            # save current_feature to dataset.csv
            os.makedirs(os.path.dirname("dataset.csv") or ".", exist_ok=True)
            row = ",".join([str(args.record)] + [f"{v:.6f}" for v in current_feature])
            with open('dataset.csv', 'a') as fh:
                fh.write(row + "\n")
            print(f"Saved sample for '{args.record}' (total features len={len(current_feature)})")

        # If training requested and user pressed 't', break loop and train
        if args.train and key == ord('t'):
            print("Starting training...")
            break

    cap.release()
    cv2.destroyAllWindows()

    # Cleanup shared memory
    try:
        shm.close()
        shm.unlink()
    except Exception as e:
        print(f"Error cleaning up shared memory: {e}")
    
    try:
        shm_cords.close()
        shm_cords.unlink()
    except Exception as e:
        print(f"Error cleaning up cords shared memory: {e}")

    # If training flag passed, train a classifier from dataset.csv
    if args.train:
        data_path = 'dataset.csv'
        if not os.path.exists(data_path):
            print(f"No dataset found at {data_path}. Record samples first using --record LABEL and pressing 's' to save.")
            return

        # Load dataset: rows label,f1,f2,...
        labels = []
        features = []
        print("\nLoading dataset...")
        start_time = time.time()
        with open(data_path, 'r') as fh:
            for line in fh:
                parts = line.strip().split(',')
                if len(parts) < 2:
                    continue
                labels.append(parts[0])
                feats = list(map(float, parts[1:]))
                features.append(feats)

        load_time = time.time() - start_time
        # Show dataset stats
        from collections import Counter
        class_counts = Counter(labels)
        print(f"\nDataset loaded in {load_time:.2f}s:")
        print(f"Total samples: {len(labels)}")
        print("Samples per class:")
        for label, count in sorted(class_counts.items()):
            print(f"  {label}: {count}")

        # Validate consistent feature length
        lengths = set(len(f) for f in features)
        if len(lengths) != 1:
            print(f"Inconsistent feature lengths in {data_path}: {lengths}. Clean or re-record data so all rows have the same feature count.")
            return

        X = np.array(features)
        y = np.array(labels)

        if RandomForestClassifier is None:
            print("scikit-learn is not installed in this environment. Install scikit-learn to enable training.")
            return

        print("\nTraining RandomForest classifier...")
        train_start = time.time()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        train_time = time.time() - train_start

        print(f"\nTraining completed in {train_time:.2f}s")
        print("\nClassification report:")
        print(classification_report(y_test, y_pred))

        # Save model
        save_start = time.time()
        with open(args.model_path, 'wb') as f:
            pickle.dump(clf, f)
        save_time = time.time() - save_start
        print(f"\nModel saved to {args.model_path} in {save_time:.2f}s")
        print(f"Total time: {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    hand_main()
