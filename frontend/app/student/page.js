"use client";

import { useContext, useState, useEffect } from "react";
import { StudentContext } from "@/context/StudentContext";
import { useRouter } from "next/navigation";
import { getInterests } from "@/services/api";
import ThinkerLogo from "@/components/ThinkerLogo";

const CAREER_OPTIONS = [
  { value: "Technology", label: "Technology" },
  { value: "Business", label: "Business" },
  { value: "Healthcare", label: "Healthcare" },
  { value: "Education", label: "Education" },
  { value: "Arts", label: "Arts & Design" },
  { value: "None", label: "None / Not sure" },
];

export default function StudentPage() {
  const { student, setStudent, clearData } = useContext(StudentContext);
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [interests, setInterests] = useState([]);
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [otherInterestInput, setOtherInterestInput] = useState("");
  const [otherInterests, setOtherInterests] = useState([]);

  // Fetch interests on mount
  useEffect(() => {
    getInterests()
      .then((data) => setInterests(data))
      .catch(() => setErrorMessage("Failed to load interests. Please refresh."));
  }, []);

  const handleNext = () => {
    setErrorMessage("");

    if (step === 1) {
      if (!student.fullName.trim()) {
        setErrorMessage("Please enter your full name.");
        return;
      }
      setStep(2);
    } else if (step === 2) {
      setStep(3);
    }
  };

  const handleBack = () => {
    setErrorMessage("");
    setStep((prev) => Math.max(1, prev - 1));
  };

  const toggleInterest = (interestId) => {
    setSelectedInterests((prev) =>
      prev.includes(interestId)
        ? prev.filter((id) => id !== interestId)
        : [...prev, interestId]
    );
  };

  const addOtherInterest = () => {
    const text = otherInterestInput.trim();
    if (!text) return;
    if (otherInterests.includes(text)) return;
    setOtherInterests((prev) => [...prev, text]);
    setOtherInterestInput("");
  };

  const removeOtherInterest = (text) => {
    setOtherInterests((prev) => prev.filter((t) => t !== text));
  };

  const handleSubmit = async () => {
    // Validate at least one interest (predefined or other)
    if (selectedInterests.length === 0 && otherInterests.length === 0) {
      setErrorMessage("Please select at least one interest or add a custom interest.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const interestsPayload = [
        ...selectedInterests.map((interest_id) => ({ interest_id })),
        ...otherInterests.map((other_interest) => ({ other_interest })),
      ];

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/students/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: student.fullName.trim(),
          email: student.email.trim() || null,
          preferred_career: student.preferredCareer || null,
          interests: interestsPayload,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail;
        throw new Error(detail || "Unable to register student. Please try again.");
      }

      setStudent((currentStudent) => ({
        ...currentStudent,
        studentId: data.id,
        interests: interestsPayload,
      }));

      router.push("/assessment");
    } catch (error) {
      setErrorMessage(error.message || "Unable to connect to the server. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalSteps = 3;

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-linear-to-r from-[#cdffd8] to-[#94b9ff] px-6 py-24">
      {/* LOGO */}
      <div className="absolute left-8 top-5 md:left-29">
        <ThinkerLogo />
      </div>

      {/* PROGRESS INDICATOR */}
      <div className="absolute top-5 right-8 hidden md:block">
        <div className="flex items-center gap-2 text-sm font-medium text-[#111827]">
          {Array.from({ length: totalSteps }, (_, i) => i + 1).map((s) => (
            <span
              key={s}
              className={`w-8 h-8 rounded-full flex items-center justify-center transition ${
                s < step
                  ? "bg-[#283d7a] text-white"
                  : s === step
                  ? "bg-[#50505A] text-white"
                  : "bg-gray-300 text-gray-500"
              }`}
            >
              {s}
            </span>
          ))}
        </div>
        <p className="text-xs text-gray-500 text-right mt-1">Step {step} of {totalSteps}</p>
      </div>

      {/* REGISTRATION FORM */}
      <div className="w-full max-w-2xl rounded-2xl bg-[#fffdf2] px-7 py-10 shadow-sm md:px-10 md:py-12">
        {/* HEADING */}
        <h2 className="text-3xl font-bold text-[#111827] md:text-4xl">
          Let's set up your profile
        </h2>

        <p className="mt-2 text-sm font-medium text-[#111827]">
          Tell us a little about yourself so we can personalize your
          assessment and recommendations.
        </p>

        {/* STEP 1: BASIC INFO */}
        {step === 1 && (
          <div className="mt-8 space-y-5" data-step={1}>
            {/* FULL NAME */}
            <div>
              <label className="mb-2 block text-sm font-semibold text-[#111827]">
                Full Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                className="w-full rounded-full border border-gray-400 bg-transparent px-5 py-3 text-sm outline-none transition focus:border-[#2F4385]"
                placeholder="Enter your full name"
                value={student.fullName}
                onChange={(e) =>
                  setStudent((currentStudent) => ({
                    ...currentStudent,
                    fullName: e.target.value,
                  }))
                }
                autoFocus
              />
            </div>

            {/* EMAIL */}
            <div>
              <label className="mb-2 block text-sm font-semibold text-[#111827]">
                Email Address
                <span className="ml-2 font-normal text-gray-500">(Optional)</span>
              </label>
              <input
                type="email"
                className="w-full rounded-full border border-gray-400 bg-transparent px-5 py-3 text-sm outline-none transition focus:border-[#2F4385]"
                placeholder="Enter your email address"
                value={student.email}
                onChange={(e) =>
                  setStudent((currentStudent) => ({
                    ...currentStudent,
                    email: e.target.value,
                  }))
                }
              />
              <p className="mt-2 text-xs text-gray-500">
                You can leave this blank if you don't want to provide an email.
              </p>
            </div>
          </div>
        )}

        {/* STEP 2: PREFERRED CAREER */}
        {step === 2 && (
          <div className="mt-8 space-y-5" data-step={2}>
            <p className="text-sm text-gray-600">
              What career path interests you most? This helps us tailor your recommendations.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {CAREER_OPTIONS.map((career) => (
                <button
                  key={career.value}
                  type="button"
                  onClick={() =>
                    setStudent((currentStudent) => ({
                      ...currentStudent,
                      preferredCareer: career.value === "None" ? "" : career.value,
                    }))
                  }
                  className={`rounded-full border-2 px-5 py-3 text-sm font-semibold transition ${
                    student.preferredCareer === (career.value === "None" ? "" : career.value)
                      ? "bg-[#283d7a] text-white border-[#283d7a]"
                      : "bg-transparent text-[#111827] border-gray-400 hover:bg-white hover:border-[#283d7a]"
                  }`}
                >
                  {career.label}
                </button>
              ))}
            </div>
            <p className="mt-2 text-xs text-gray-500 text-center">
              Select one option. You can choose "None / Not sure" if undecided.
            </p>
          </div>
        )}

        {/* STEP 3: INTERESTS */}
        {step === 3 && (
          <div className="mt-8 space-y-5" data-step={3}>
            <p className="text-sm text-gray-600">
              Select your interests (multiple allowed). These help match you with programs.
            </p>

            {/* Predefined Interests */}
            <div className="flex flex-wrap gap-2">
              {interests.map((interest) => (
                <button
                  key={interest.id}
                  type="button"
                  onClick={() => toggleInterest(interest.id)}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                    selectedInterests.includes(interest.id)
                      ? "bg-[#283d7a] text-white"
                      : "bg-transparent text-[#111827] border border-gray-400 hover:bg-white"
                  }`}
                >
                  {interest.name}
                </button>
              ))}
            </div>

            {/* Other Interest Input */}
            <div className="flex gap-2">
              <input
                type="text"
                className="flex-1 rounded-full border border-gray-400 bg-transparent px-5 py-2 text-sm outline-none transition focus:border-[#2F4385]"
                placeholder="Add a custom interest..."
                value={otherInterestInput}
                onChange={(e) => setOtherInterestInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addOtherInterest())}
              />
              <button
                type="button"
                onClick={addOtherInterest}
                className="rounded-full bg-[#50505A] px-4 py-2 text-sm font-bold text-white transition hover:bg-[#3f3f47]"
                disabled={!otherInterestInput.trim()}
              >
                Add
              </button>
            </div>

            {/* Other Interests Tags */}
            {otherInterests.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {otherInterests.map((text) => (
                  <span
                    key={text}
                    className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
                  >
                    {text}
                    <button
                      type="button"
                      onClick={() => removeOtherInterest(text)}
                      className="text-gray-500 hover:text-red-500"
                      aria-label="Remove"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}

            <p className="mt-2 text-xs text-gray-500">
              Select at least one interest (predefined or custom) to continue.
            </p>
          </div>
        )}

        {/* ERROR MESSAGE */}
        {errorMessage && (
          <p className="mt-5 text-sm font-medium text-red-600">{errorMessage}</p>
        )}

        {/* NAVIGATION BUTTONS */}
        <div className="mt-8 flex justify-between">
          <button
            type="button"
            onClick={handleBack}
            disabled={step === 1}
            className={`rounded-full px-9 py-3 text-sm font-bold transition ${
              step === 1
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-white text-[#50505A] border border-gray-400 hover:bg-gray-50"
            }`}
          >
            BACK
          </button>

          <button
            type="button"
            onClick={step === totalSteps ? handleSubmit : handleNext}
            disabled={isSubmitting}
            className={`rounded-full px-9 py-3 text-sm font-bold text-white transition ${
              step === totalSteps
                ? "bg-[#50505A] hover:bg-[#3f3f47]"
                : "bg-[#283d7a] hover:bg-[#1f315f]"
            } disabled:cursor-not-allowed disabled:opacity-60`}
          >
            {isSubmitting
              ? "SAVING..."
              : step === totalSteps
              ? "REGISTER & START ASSESSMENT"
              : "CONTINUE"}
          </button>
        </div>
      </div>
    </main>
  );
}