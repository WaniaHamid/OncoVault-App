import os
import sys
import tempfile
import time
import pythoncom
import win32com.client

# Ensure oncovault_nlp directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transcription.whisper_service import WhisperService

BENCHMARK_SENTENCES = [
    # 1. Critical "bruising" test case
    {
        "text": "The patient has significant bruising.",
        "key_terms": ["bruising"]
    },
    # 2. Symptoms & Bruising combination
    {
        "text": "The patient has significant bruising, persistent weakness, night sweats, and swollen painless lymph nodes.",
        "key_terms": ["bruising", "weakness", "night sweats", "lymph nodes"]
    },
    # 3. Negated fever & present bruising
    {
        "text": "The patient denies fever and bone pain but reports significant bruising and persistent fatigue.",
        "key_terms": ["fever", "bone pain", "bruising", "fatigue"]
    },
    # 4. Shortness of breath and bleeding
    {
        "text": "Patient presents with shortness of breath and significant bleeding from gums.",
        "key_terms": ["shortness of breath", "bleeding"]
    },
    # 5. Frequent infections and itchy skin
    {
        "text": "Patient reports frequent infections and itchy skin rash over the abdomen.",
        "key_terms": ["frequent infections", "itchy skin", "rash"]
    },
    # 6. Loss of appetite and jaundice
    {
        "text": "Patient has loss of appetite, nausea, and noticeable jaundice in eyes.",
        "key_terms": ["loss of appetite", "nausea", "jaundice"]
    },
    # 7. Liver and oral cavity
    {
        "text": "Physical examination reveals enlarged liver and oral cavity changes.",
        "key_terms": ["enlarged liver", "oral cavity changes"]
    },
    # 8. Vision blurring and smoking history
    {
        "text": "Patient has vision blurring and a long smoking history.",
        "key_terms": ["vision blurring", "smoking"]
    },
    # 9. CBC: WBC and Hemoglobin
    {
        "text": "White blood cell count is 14.5 and hemoglobin is 10.2 grams per deciliter.",
        "key_terms": ["white blood cell count", "14.5", "hemoglobin", "10.2"]
    },
    # 10. CBC: Platelets and Hematocrit
    {
        "text": "Platelets are 110 and hematocrit is 32 percent.",
        "key_terms": ["platelets", "110", "hematocrit", "32"]
    },
    # 11. Differential: Neutrophils and Lymphocytes
    {
        "text": "Absolute neutrophils are 3.2 and lymphocytes are 45 percent.",
        "key_terms": ["neutrophils", "3.2", "lymphocytes", "45"]
    },
    # 12. Differential: Monocytes, Eosinophils, Basophils
    {
        "text": "Monocytes are 8 percent, eosinophils 2 percent, and basophils 1 percent.",
        "key_terms": ["monocytes", "eosinophils", "basophils"]
    },
    # 13. RDW parameters
    {
        "text": "Laboratory shows elevated RDW-SD of 48 and RDW-CV of 16 percent.",
        "key_terms": ["rdw-sd", "rdw-cv"]
    },
    # 14. Blast percentage
    {
        "text": "Peripheral smear demonstrates blast cell percentage of 12 percent.",
        "key_terms": ["blast", "12"]
    },
    # 15. Leukemia classification (AML)
    {
        "text": "Patient diagnosed with acute myeloid leukemia AML in intermediate risk category.",
        "key_terms": ["acute myeloid leukemia", "aml", "intermediate"]
    },
    # 16. Leukemia classification (ALL)
    {
        "text": "Confirmed acute lymphoblastic leukemia ALL undergoing induction.",
        "key_terms": ["acute lymphoblastic leukemia", "all", "induction"]
    },
    # 17. Bone marrow biopsy
    {
        "text": "Bone marrow biopsy reveals hypercellular marrow with 30 percent leukemic blasts.",
        "key_terms": ["bone marrow biopsy", "blasts"]
    },
    # 18. Chemotherapy regimen
    {
        "text": "Initiating 7 plus 3 chemotherapy regimen with cytarabine and daunorubicin.",
        "key_terms": ["chemotherapy", "cytarabine"]
    }
]

def synthesize_audio_to_file(text: str, output_wav_path: str) -> None:
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    # 39 = SAFT16kHz16BitMono
    stream.Format.Type = 39
    stream.Open(output_wav_path, 3, False)
    speaker.AudioOutputStream = stream
    speaker.Speak(text)
    stream.Close()
    pythoncom.CoUninitialize()

def run_benchmark():
    print("=" * 80)
    print("ONCOVAULT CLINICAL ASR ACCURACY BENCHMARK — WHISPER SPEECH-TO-TEXT")
    print("=" * 80)
    
    whisper_service = WhisperService.get_instance()
    print(f"Loaded Whisper Model: {whisper_service.model_size}\n")
    
    total_sentences = len(BENCHMARK_SENTENCES)
    total_key_terms = 0
    recognized_key_terms = 0
    results_summary = []
    
    start_time_all = time.time()
    
    for idx, item in enumerate(BENCHMARK_SENTENCES, 1):
        expected_text = item["text"]
        key_terms = item["key_terms"]
        
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_wav_path = temp_wav.name
        temp_wav.close()
        
        try:
            synthesize_audio_to_file(expected_text, temp_wav_path)
            
            t0 = time.time()
            transcription_res = whisper_service.transcribe(temp_wav_path, language="en")
            latency = time.time() - t0
            
            actual_text = transcription_res["transcript"]
            
            actual_lower = actual_text.lower()
            matched_terms = []
            missed_terms = []
            
            for term in key_terms:
                total_key_terms += 1
                t_clean = term.lower().replace("-", " ")
                if term.lower() in actual_lower or t_clean in actual_lower.replace("-", " "):
                    recognized_key_terms += 1
                    matched_terms.append(term)
                else:
                    missed_terms.append(term)
                    
            status_str = "PASS" if len(missed_terms) == 0 else "PARTIAL"
            results_summary.append({
                "id": idx,
                "expected": expected_text,
                "actual": actual_text,
                "key_terms": key_terms,
                "matched": matched_terms,
                "missed": missed_terms,
                "latency_s": round(latency, 2),
                "status": status_str
            })
            
            print(f"[{idx:02d}/{total_sentences:02d}] Status: {status_str} ({latency:.2f}s)")
            print(f"  Expected: \"{expected_text}\"")
            print(f"  Actual:   \"{actual_text}\"")
            print(f"  Key Terms Matched: {matched_terms}")
            if missed_terms:
                print(f"  Key Terms MISSED:  {missed_terms}")
            print("-" * 80)
            
        finally:
            if os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except Exception:
                    pass
                    
    total_time = time.time() - start_time_all
    accuracy_pct = (recognized_key_terms / total_key_terms) * 100.0 if total_key_terms > 0 else 0.0
    
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY RESULTS")
    print("=" * 80)
    print(f"Total Sentences Evaluated: {total_sentences}")
    print(f"Total Medical Key Terms:   {total_key_terms}")
    print(f"Key Terms Correct:         {recognized_key_terms} / {total_key_terms}")
    print(f"Clinical Term Accuracy:    {accuracy_pct:.2f}%")
    print(f"Total Time:                {total_time:.2f}s (Avg {total_time/total_sentences:.2f}s/sentence)")
    print("=" * 80)
    
    bruising_test = results_summary[0]
    print(f"\nCRITICAL TEST #1: \"bruising\" verification:")
    print(f"  Input:    {bruising_test['expected']}")
    print(f"  Output:   {bruising_test['actual']}")
    print(f"  Bruising in Output: {'YES (SUCCESS)' if 'bruising' in bruising_test['actual'].lower() else 'NO (FAILED)'}")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
